from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, cast
import collections
import datetime
import logging
import time

from botocore.config import Config
from botocore.exceptions import ClientError
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from lru import LRU
import boto3

from .. import settings
from ..abc import (
    ConsumerBackend,
    OffsetStoreBackend,
    ProducerBackend,
    Record,
    RecordMetadata,
)
from . import get_offset_backend

if TYPE_CHECKING:
    from mypy_boto3_kinesis import KinesisClient
    from mypy_boto3_kinesis.type_defs import (
        GetRecordsOutputTypeDef,
        PutRecordOutputTypeDef,
    )

logger = logging.getLogger(__name__)

ShardID = str
ShardIterator = str

DEFAULT_KINESIS_CONNECT_TIMEOUT = 5
DEFAULT_KINESIS_READ_TIMEOUT = 10
DEFAULT_KINESIS_MAX_ATTEMPTS = 3


class _ExpiredShardIteratorError(Exception):
    pass


class KinesisClientConfig(TypedDict):
    region_name: str
    config: Config


class PutRecordKwargs(TypedDict):
    StreamName: str
    Data: bytes
    PartitionKey: str
    SequenceNumberForOrdering: NotRequired[str]


def _merge_client_kwargs(base: KinesisClientConfig, extra: Mapping[str, Any]) -> None:
    if not extra:
        return
    merged: dict[str, Any] = dict(extra)
    if "config" in merged:
        user_config = merged.pop("config")
        if isinstance(user_config, Mapping):
            user_config = Config(**user_config)
        elif not isinstance(user_config, Config):
            raise ImproperlyConfigured("Kinesis client 'config' must be a botocore.config.Config instance or a mapping of Config options.")
        user_retries: Mapping[str, Any] | None = getattr(user_config, "retries", None)
        merged_config = base["config"].merge(user_config)
        if user_retries:
            base_retries = getattr(base["config"], "retries", None) or {}
            retries = dict(base_retries)
            if {"max_attempts", "total_max_attempts"} & user_retries.keys():
                retries.pop("max_attempts", None)
                retries.pop("total_max_attempts", None)
            retries.update(user_retries)
            merged_config = merged_config.merge(Config(retries=cast(Any, retries)))
        base["config"] = merged_config
    base.update(merged)  # type: ignore[typeddict-item]


class KinesisBase:
    _client: KinesisClient | None = None

    @property
    def client(self) -> KinesisClient:
        if not self._client:
            kwargs = self._get_client_config()
            self._client = boto3.client("kinesis", **kwargs)
        return self._client

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def _get_client_config(self) -> KinesisClientConfig:
        connect_timeout = settings.get(
            "KINESIS_CONNECT_TIMEOUT",
            DEFAULT_KINESIS_CONNECT_TIMEOUT,
        )
        read_timeout = settings.get(
            "KINESIS_READ_TIMEOUT",
            DEFAULT_KINESIS_READ_TIMEOUT,
        )
        max_attempts = settings.get(
            "KINESIS_MAX_ATTEMPTS",
            DEFAULT_KINESIS_MAX_ATTEMPTS,
        )
        kwargs = KinesisClientConfig(
            region_name=settings.get_aws_region(),
            config=Config(
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                retries={"total_max_attempts": max_attempts},
            ),
        )
        _merge_client_kwargs(kwargs, settings.get("KINESIS_KWARGS", {}))
        return kwargs


class ModelOffsetStore(OffsetStoreBackend):
    @staticmethod
    def _get_region(consumer: ConsumerBackend) -> str:
        if isinstance(consumer, KinesisBase):
            return consumer.client.meta.region_name
        return settings.get_aws_region()

    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        KinesisOffset = apps.get_model(app_label="logpipe", model_name="KinesisOffset")
        region = self._get_region(consumer)
        logger.debug(
            f'Commit offset "{message.offset}" for region "{region}", stream "{message.topic}", shard "{message.partition}" to {self.__class__.__name__}'
        )
        obj, _created = KinesisOffset.objects.get_or_create(region=region, stream=message.topic, shard=message.partition)
        obj.sequence_number = message.offset
        obj.save()

    def seek(self, consumer: ConsumerBackend, stream: str, shard: str) -> None:
        KinesisOffset = apps.get_model(app_label="logpipe", model_name="KinesisOffset")
        region = self._get_region(consumer)
        try:
            obj = KinesisOffset.objects.get(region=region, stream=stream, shard=shard)
            logger.debug(f'Seeking to offset "{obj.sequence_number}" on region "{region}", stream "{stream}", partition "{shard}"')
            consumer.seek_to_sequence_number(shard, obj.sequence_number)
        except KinesisOffset.DoesNotExist:
            logger.debug(f'Seeking to beginning of region "{region}", stream "{stream}", partition "{shard}"')
            consumer.seek_to_sequence_number(shard, None)


class Consumer(KinesisBase, ConsumerBackend):
    def __init__(self, topic_name: str, **kwargs: Any):
        self.topic_name = topic_name
        self.client_kwargs = kwargs

        self.shards: collections.deque[ShardID] = collections.deque()
        self.records: collections.deque[Record] = collections.deque()
        self.shard_iters: dict[ShardID, ShardIterator] = {}
        self.last_sequence_numbers: dict[ShardID, str] = {}
        self.initial_seek_timestamps: dict[ShardID, datetime.datetime] = {}

        shards = self._list_shard_ids()
        logger.debug("Found %d kinesis shards.", len(shards))
        backend = get_offset_backend()
        for shard in shards:
            self.shards.append(shard)
            backend.seek(self, self.topic_name, shard)

    def seek_to_sequence_number(self, shard: str, sequence_number: str | None = None) -> None:
        if sequence_number is None:
            iterator_type = settings.get("KINESIS_SHARD_ITERATOR_TYPE", default="TRIM_HORIZON")
            if iterator_type == "LATEST":
                self.initial_seek_timestamps.setdefault(shard, datetime.datetime.now(datetime.UTC))
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType=iterator_type,
            )
        else:
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType="AFTER_SEQUENCE_NUMBER",
                StartingSequenceNumber=sequence_number,
            )
        self.shard_iters[shard] = resp["ShardIterator"]

    def _refresh_shard_iterator(self, shard: ShardID) -> None:
        last_seq = self.last_sequence_numbers.get(shard)
        if last_seq is not None:
            self.seek_to_sequence_number(shard, last_seq)
        elif shard in self.initial_seek_timestamps:
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType="AT_TIMESTAMP",
                Timestamp=self.initial_seek_timestamps[shard],
            )
            self.shard_iters[shard] = resp["ShardIterator"]
        else:
            get_offset_backend().seek(self, self.topic_name, shard)

    def _get_client_config(self) -> KinesisClientConfig:
        kwargs = super()._get_client_config()
        _merge_client_kwargs(kwargs, settings.get("KINESIS_CONSUMER_KWARGS", {}))
        return kwargs

    def __iter__(self) -> Consumer:
        return self

    def __next__(self) -> Record:
        # Try and load records. Keep trying until either (1) we have some records or (2) current_lag drops to 0
        while len(self.records) <= 0:
            # Load a page from each shard and sum the shard lags
            current_lag = 0
            for i in range(len(self.shards)):
                current_lag += self._load_next_page()

            # If all shards report 0 lag, then give up trying to load records
            if current_lag <= 0:
                break

        # If we've tried all the shards and still don't have any records, stop iteration
        if len(self.records) == 0:
            raise StopIteration()

        # Return the left most record in the queue
        return self.records.popleft()

    def _load_next_page(self) -> int:
        # Load a page from the left-most shard in the queue
        try:
            shard = self.shards.popleft()
        except IndexError:
            return 0

        # Get the next shard iterator for the shard
        shard_iter = self.shard_iters.get(shard)
        if not shard_iter:
            return 0
        # Re-queue now; only a closed shard (NextShardIterator=None) removes it below.
        self.shards.append(shard)

        # Fetch the records from Kinesis
        logger.debug("Loading page of records from %s.%s", self.topic_name, shard)
        fetch_limit = settings.get("KINESIS_FETCH_LIMIT", 25)
        try:
            response = self._get_records(shard_iter, fetch_limit)
        except _ExpiredShardIteratorError:
            try:
                self._refresh_shard_iterator(shard)
                response = self._get_records(self.shard_iters[shard], fetch_limit)
            except ClientError as e:
                logger.warning(
                    "Failed to refresh expired shard iterator for %s.%s: %s. Sleeping for 5 seconds.",
                    self.topic_name,
                    shard,
                    e,
                )
                time.sleep(5)
                return 0
            except _ExpiredShardIteratorError:
                logger.warning(
                    "Refreshed shard iterator for %s.%s expired before records could be fetched.",
                    self.topic_name,
                    shard,
                )
                return 0
        if response is None:
            return 0

        # This default value is mostly just for testing with Moto. Real Kinesis should always return a value for MillisBehindLatest.
        num_records = len(response["Records"])
        if "MillisBehindLatest" in response:
            current_stream_lag = response["MillisBehindLatest"]
        else:
            current_stream_lag = 0 if num_records == 0 else 1
        logger.debug(f"Loaded {num_records} records from {self.topic_name}.{shard}. Currently {current_stream_lag}ms behind stream head.")

        # Add the records page into the queue
        timestamp = (time.time() * 1000) - current_stream_lag
        for r in response["Records"]:
            record = Record(
                topic=self.topic_name,
                partition=shard,
                offset=r["SequenceNumber"],
                timestamp=timestamp,
                key=r["PartitionKey"],
                value=r["Data"],
            )
            self.records.append(record)
            self.last_sequence_numbers[shard] = r["SequenceNumber"]

        # Save the next shard iterator, or remove the closed shard from the fetch pool.
        if response.get("NextShardIterator", None):
            self.shard_iters[shard] = response["NextShardIterator"]
        else:
            self.shard_iters.pop(shard, None)
            self.shards.remove(shard)
            logger.info(f"Shard {self.topic_name}.{shard} has been closed. Removing it from the fetch pool.")

        return current_stream_lag

    def _get_records(
        self,
        shard_iter: ShardIterator,
        fetch_limit: int,
    ) -> GetRecordsOutputTypeDef | None:
        retries = settings.get("KINESIS_MAX_FETCH_RETRIES", 1)
        i = 0
        while i <= retries:
            try:
                response = self.client.get_records(ShardIterator=shard_iter, Limit=fetch_limit)
                return response
            except ClientError as e:
                error = e.response.get("Error") or {}
                code = error.get("Code", "")
                if code == "ExpiredIteratorException":
                    logger.warning("Caught ExpiredIteratorException; shard iterator must be refreshed.")
                    raise _ExpiredShardIteratorError() from e
                if code == "ProvisionedThroughputExceededException":
                    logger.warning("Caught ProvisionedThroughputExceededException. Sleeping for 5 seconds.")
                    time.sleep(5)
                else:
                    logger.warning(
                        "Received %s from AWS API: %s. Sleeping for 5 seconds.",
                        code or "ClientError",
                        error.get("Message", ""),
                    )
                    time.sleep(5)
                    return None
            i += 1
        logger.warning(f"After {i} attempts, couldn't get records from Kinesis. Giving up.")
        return None

    def _list_shard_ids(self) -> list[ShardID]:
        resp = self.client.describe_stream(StreamName=self.topic_name)
        return [shard["ShardId"] for shard in resp["StreamDescription"]["Shards"]]


class Producer(KinesisBase, ProducerBackend):
    _last_sequence_numbers: LRU[str, dict[str, str]] = LRU(settings.get("KINESIS_SEQ_NUM_CACHE_SIZE", 1000))

    def _get_client_config(self) -> KinesisClientConfig:
        kwargs = super()._get_client_config()
        _merge_client_kwargs(kwargs, settings.get("KINESIS_PRODUCER_KWARGS", {}))
        return kwargs

    def send(self, topic_name: str, key: str, value: bytes) -> RecordMetadata | None:
        kwargs = PutRecordKwargs(
            StreamName=topic_name,
            Data=value,
            PartitionKey=key,
        )

        if topic_name not in self._last_sequence_numbers:
            self._last_sequence_numbers[topic_name] = {}
        last_seq_num = self._last_sequence_numbers[topic_name].get(key)
        if last_seq_num:
            kwargs["SequenceNumberForOrdering"] = last_seq_num

        metadata = self._send_and_retry(kwargs)
        if metadata is None:
            return None

        shard_id = metadata["ShardId"]
        seq_num = str(metadata["SequenceNumber"])
        self._last_sequence_numbers[topic_name][key] = seq_num

        return RecordMetadata(topic=topic_name, partition=shard_id, offset=seq_num)

    def _send_and_retry(
        self,
        data: PutRecordKwargs,
    ) -> PutRecordOutputTypeDef | None:
        retries = settings.get("KINESIS_MAX_SEND_RETRIES", 1)
        i = 0
        while i <= retries:
            try:
                metadata = self.client.put_record(**data)
                return metadata
            except ClientError as e:
                if e.response["Error"]["Code"] == "ProvisionedThroughputExceededException":
                    if i < retries:
                        logger.warning("Caught ProvisionedThroughputExceededException. Sleeping for 5 seconds.")
                        time.sleep(5)
                else:
                    logger.warning(
                        "Received %s from AWS API: %s",
                        e.response["Error"]["Code"],
                        e.response["Error"]["Message"],
                    )
            i += 1
        logger.warning(f"After {i} attempts, couldn't send message to Kinesis. Giving up.")
        return None
