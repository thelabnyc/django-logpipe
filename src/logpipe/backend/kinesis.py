from __future__ import annotations

from typing import TYPE_CHECKING, Any, NotRequired, TypedDict
import collections
import logging
import time

from botocore.exceptions import ClientError
from django.apps import apps
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


class KinesisClientConfig(TypedDict):
    region_name: str


class PutRecordKwargs(TypedDict):
    StreamName: str
    Data: bytes
    PartitionKey: str
    SequenceNumberForOrdering: NotRequired[str]


class KinesisBase:
    _client: KinesisClient | None = None

    @property
    def client(self) -> KinesisClient:
        if not self._client:
            kwargs = self._get_client_config()
            self._client = boto3.client("kinesis", **kwargs)
        return self._client

    def _get_client_config(self) -> KinesisClientConfig:
        return KinesisClientConfig(
            region_name=settings.get_aws_region(),
        )


class ModelOffsetStore(OffsetStoreBackend):
    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        KinesisOffset = apps.get_model(app_label="logpipe", model_name="KinesisOffset")
        region = settings.get_aws_region()
        logger.debug(
            'Commit offset "%s" for region "%s", stream "%s", shard "%s" to %s'
            % (
                message.offset,
                region,
                message.topic,
                message.partition,
                self.__class__.__name__,
            )
        )
        obj, created = KinesisOffset.objects.get_or_create(
            region=region, stream=message.topic, shard=message.partition
        )
        obj.sequence_number = message.offset
        obj.save()

    def seek(self, consumer: ConsumerBackend, stream: str, shard: str) -> None:
        KinesisOffset = apps.get_model(app_label="logpipe", model_name="KinesisOffset")
        region = settings.get_aws_region()
        try:
            obj = KinesisOffset.objects.get(
                region=settings.get_aws_region(), stream=stream, shard=shard
            )
            logger.debug(
                'Seeking to offset "%s" on region "%s", stream "%s", partition "%s"'
                % (obj.sequence_number, region, stream, shard)
            )
            consumer.seek_to_sequence_number(shard, obj.sequence_number)
        except KinesisOffset.DoesNotExist:
            logger.debug(
                'Seeking to beginning of region "%s", stream "%s", partition "%s"'
                % (region, stream, shard)
            )
            consumer.seek_to_sequence_number(shard, None)


class Consumer(KinesisBase, ConsumerBackend):
    def __init__(self, topic_name: str, **kwargs: Any):
        self.topic_name = topic_name
        self.client_kwargs = kwargs

        self.shards: collections.deque[ShardID] = collections.deque()
        self.records: collections.deque[Record] = collections.deque()
        self.shard_iters: dict[ShardID, ShardIterator] = {}

        shards = self._list_shard_ids()
        logger.debug("Found %d kinesis shards.", len(shards))
        backend = get_offset_backend()
        for shard in shards:
            self.shards.append(shard)
            backend.seek(self, self.topic_name, shard)

    def seek_to_sequence_number(
        self, shard: str, sequence_number: str | None = None
    ) -> None:
        if sequence_number is None:
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType=settings.get(
                    "KINESIS_SHARD_ITERATOR_TYPE", default="TRIM_HORIZON"
                ),
            )
        else:
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType="AFTER_SEQUENCE_NUMBER",
                StartingSequenceNumber=sequence_number,
            )
        self.shard_iters[shard] = resp["ShardIterator"]

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
        shard_iter = self.shard_iters.pop(shard, None)
        if not shard_iter:
            return 0

        # Fetch the records from Kinesis
        logger.debug("Loading page of records from %s.%s", self.topic_name, shard)
        fetch_limit = settings.get("KINESIS_FETCH_LIMIT", 25)
        response = self._get_records(shard_iter, fetch_limit)
        if response is None:
            return 0

        # This default value is mostly just for testing with Moto. Real Kinesis should always return a value for MillisBehindLatest.
        num_records = len(response["Records"])
        if "MillisBehindLatest" in response:
            current_stream_lag = response["MillisBehindLatest"]
        else:
            current_stream_lag = 0 if num_records == 0 else 1
        logger.debug(
            "Loaded {} records from {}.{}. Currently {}ms behind stream head.".format(
                num_records, self.topic_name, shard, current_stream_lag
            )
        )

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

        # Add the shard back to the right of the queue and save the shard iterator for next time we need
        # to get records from this shard. If NextShardIterator is None, the shard has been closed and
        # we should remove it from the pool.
        if response.get("NextShardIterator", None):
            self.shard_iters[shard] = response["NextShardIterator"]
            self.shards.append(shard)
        else:
            logger.info(
                "Shard {}.{} has been closed. Removing it from the fetch pool.".format(
                    self.topic_name, shard
                )
            )

        return current_stream_lag

    def _get_records(
        self,
        shard_iter: ShardIterator,
        fetch_limit: int,
        retries: int = 1,
    ) -> GetRecordsOutputTypeDef | None:
        i = 0
        while i <= retries:
            try:
                response = self.client.get_records(
                    ShardIterator=shard_iter, Limit=fetch_limit
                )
                return response
            except ClientError as e:
                if (
                    e.response["Error"]["Code"]
                    == "ProvisionedThroughputExceededException"
                ):
                    logger.warning(
                        "Caught ProvisionedThroughputExceededException. Sleeping for 5 seconds."
                    )
                    time.sleep(5)
                else:
                    logger.warning(
                        "Received {} from AWS API: {}".format(
                            e.response["Error"]["Code"], e.response["Error"]["Message"]
                        )
                    )
            i += 1
        logger.warning(
            f"After {i} attempts, couldn't get records from Kinesis. Giving up."
        )
        return None

    def _list_shard_ids(self) -> list[ShardID]:
        resp = self.client.describe_stream(StreamName=self.topic_name)
        return [shard["ShardId"] for shard in resp["StreamDescription"]["Shards"]]


class Producer(KinesisBase, ProducerBackend):
    _last_sequence_numbers: LRU[str, dict[str, str]] = LRU(
        settings.get("KINESIS_SEQ_NUM_CACHE_SIZE", 1000)
    )

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
        self, data: PutRecordKwargs, retries: int = 1
    ) -> PutRecordOutputTypeDef | None:
        i = 0
        while i <= retries:
            try:
                metadata = self.client.put_record(**data)
                return metadata
            except ClientError as e:
                if (
                    e.response["Error"]["Code"]
                    == "ProvisionedThroughputExceededException"
                ):
                    logger.warning(
                        "Caught ProvisionedThroughputExceededException. Sleeping for 5 seconds."
                    )
                    time.sleep(5)
                else:
                    logger.warning(
                        "Received %s from AWS API: %s",
                        e.response["Error"]["Code"],
                        e.response["Error"]["Message"],
                    )
            i += 1
        logger.warning(
            f"After {i} attempts, couldn't send message to Kinesis. Giving up."
        )
        return None
