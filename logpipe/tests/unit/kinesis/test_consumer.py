from typing import Any
from unittest.mock import MagicMock, call, patch

from botocore.exceptions import ClientError, ParamValidationError, ReadTimeoutError
from django.test import override_settings
from moto import mock_aws
from rest_framework.exceptions import ValidationError
import boto3

from logpipe import Consumer
from logpipe.backend.kinesis import (
    DEFAULT_KINESIS_CONNECT_TIMEOUT,
    DEFAULT_KINESIS_MAX_ATTEMPTS,
    DEFAULT_KINESIS_READ_TIMEOUT,
)
from logpipe.exceptions import InvalidMessageError, UnknownMessageVersionError
from logpipe.models import KinesisOffset
from logpipe.tests.common import TOPIC_STATES, BaseTest

LOGPIPE = {
    "OFFSET_BACKEND": "logpipe.backend.kinesis.ModelOffsetStore",
    "PRODUCER_BACKEND": "logpipe.backend.kinesis.Producer",
    "CONSUMER_BACKEND": "logpipe.backend.kinesis.Consumer",
}


class ConsumerTest(BaseTest):
    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_normal_consume(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )

        # Test the values sent to our serializer match the message
        def save(ser):
            self.assertEqual(ser.validated_data["code"], "NY")
            self.assertEqual(ser.validated_data["name"], "New York")

        FakeStateSerializer = self.mock_state_serializer_drf(save)

        # Consume a message
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)

        consumer.run(iter_limit=10)
        self.assertEqual(self.serializers["state"].save.call_count, 1)
        consumer.run(iter_limit=10)
        self.assertEqual(self.serializers["state"].save.call_count, 1)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_close_releases_client(self) -> None:
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        consumer = Consumer(TOPIC_STATES)
        client = consumer.consumer.client
        with patch.object(client, "close", wraps=client.close) as close:
            with consumer:
                pass
            consumer.close()
        close.assert_called_once_with()
        self.assertIsNone(consumer.consumer._client)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_consumer_uses_default_timeouts_and_get_records_handles_errors_and_restores_shards(self) -> None:
        client = self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        consumer = Consumer(TOPIC_STATES)
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer.register(FakeStateSerializer)
        boto_config = consumer.consumer.client.meta.config
        self.assertEqual(boto_config.connect_timeout, DEFAULT_KINESIS_CONNECT_TIMEOUT)
        self.assertEqual(boto_config.read_timeout, DEFAULT_KINESIS_READ_TIMEOUT)
        self.assertEqual(
            boto_config.retries,
            {"total_max_attempts": DEFAULT_KINESIS_MAX_ATTEMPTS, "mode": "standard"},
        )

        # Transport errors (which botocore's retry handler already retried inside get_records)
        # propagate directly from _get_records, while _load_next_page preserves (shard, shard_iter).
        with (
            patch.object(
                consumer.consumer.client,
                "get_records",
                side_effect=ReadTimeoutError(endpoint_url="https://kinesis.us-east-1.amazonaws.com"),
            ) as get_records_mock,
            self.assertRaises(ReadTimeoutError),
        ):
            consumer.run(iter_limit=1)
        self.assertEqual(get_records_mock.call_count, 1)
        self.assertEqual(len(consumer.consumer.shards), 1)
        self.assertEqual(len(consumer.consumer.shard_iters), 1)

        # Follow-up run after ReadTimeoutError succeeds using the preserved shard and iterator
        consumer.run(iter_limit=1)
        self.assertEqual(self.serializers["state"].save.call_count, 1)

        # Non-transport BotoCoreError raises immediately without retry
        with (
            patch.object(
                consumer.consumer.client,
                "get_records",
                side_effect=ParamValidationError(report="invalid shard iter"),
            ) as non_transport_mock,
            self.assertRaises(ParamValidationError),
        ):
            consumer.consumer._get_records("shard-iter", 10)
        self.assertEqual(non_transport_mock.call_count, 1)

        # Publish a second record and verify ClientError (ProvisionedThroughputExceededException)
        # returns None after retry without dropping the shard from the consumer.
        client.put_record(
            StreamName=TOPIC_STATES,
            Data=b'json:{"message":{"code":"PA","name":"Pennsylvania"},"version":1,"type":"us-state"}',
            PartitionKey="PA",
        )
        with (
            patch.object(
                consumer.consumer.client,
                "get_records",
                side_effect=ClientError(
                    {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "throttled"}},
                    "GetRecords",
                ),
            ) as throttle_mock,
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            consumer.run(iter_limit=1)
        self.assertEqual(throttle_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_args_list, [call(5), call(5)])
        self.assertEqual(FakeStateSerializer.call_count, 1)
        self.assertEqual(len(consumer.consumer.shards), 1)
        self.assertEqual(len(consumer.consumer.shard_iters), 1)

        # Next run succeeds because the shard and iterator were preserved
        consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 2)
        self.assertEqual(self.serializers["state"].save.call_count, 1)

    @override_settings(LOGPIPE={**LOGPIPE, "KINESIS_MAX_FETCH_RETRIES": 0})
    @mock_aws
    def test_get_records_throttled_sleeps_after_final_attempt_with_zero_fetch_retries(self) -> None:
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)

        with (
            patch.object(
                consumer.consumer.client,
                "get_records",
                side_effect=ClientError(
                    {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "throttled"}},
                    "GetRecords",
                ),
            ) as throttle_mock,
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            consumer.run(iter_limit=1)

        self.assertEqual(throttle_mock.call_count, 1)
        sleep_mock.assert_called_once_with(5)
        self.assertEqual(len(consumer.consumer.shards), 1)
        self.assertEqual(len(consumer.consumer.shard_iters), 1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE={**LOGPIPE, "KINESIS_FETCH_LIMIT": 1})
    @mock_aws
    def test_expired_shard_iterator_is_refreshed_and_resumes_from_last_sequence_number(self) -> None:
        client = self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        client.put_record(
            StreamName=TOPIC_STATES,
            Data=b'json:{"message":{"code":"PA","name":"Pennsylvania"},"version":1,"type":"us-state"}',
            PartitionKey="PA",
        )

        seen_codes: list[str] = []

        def save(ser: Any) -> None:
            seen_codes.append(ser.validated_data["code"])

        FakeStateSerializer = self.mock_state_serializer_drf(save)
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)
        raw_client = consumer.consumer.client
        real_get_records = raw_client.get_records
        expired_err = ClientError(
            {"Error": {"Code": "ExpiredIteratorException", "Message": "Iterator expired"}},
            "GetRecords",
        )

        # 1) ExpiredIteratorException before any records have been fetched re-seeks via OffsetStore
        calls_first = 0

        def get_records_expire_once(**kwargs: Any) -> Any:
            nonlocal calls_first
            calls_first += 1
            if calls_first == 1:
                raise expired_err
            return real_get_records(**kwargs)

        with (
            patch.object(raw_client, "get_records", side_effect=get_records_expire_once),
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            consumer.run(iter_limit=1)
        sleep_mock.assert_not_called()
        self.assertEqual(calls_first, 2)
        self.assertEqual(seen_codes, ["NY"])
        self.assertEqual(consumer.consumer.last_sequence_numbers.get("shardId-000000000000"), "1")

        # 2) ExpiredIteratorException after record "1" was fetched refreshes via seek_to_sequence_number("1")
        calls_second = 0

        def get_records_expire_again(**kwargs: Any) -> Any:
            nonlocal calls_second
            calls_second += 1
            if calls_second == 1:
                raise expired_err
            return real_get_records(**kwargs)

        with (
            patch.object(raw_client, "get_records", side_effect=get_records_expire_again),
            patch.object(
                consumer.consumer,
                "seek_to_sequence_number",
                wraps=consumer.consumer.seek_to_sequence_number,
            ) as seek_seq_mock,
        ):
            consumer.run(iter_limit=1)
        self.assertEqual(calls_second, 2)
        seek_seq_mock.assert_called_once_with("shardId-000000000000", "1")
        self.assertEqual(seen_codes, ["NY", "PA"])

    @override_settings(LOGPIPE={**LOGPIPE, "KINESIS_SHARD_ITERATOR_TYPE": "LATEST"})
    @mock_aws
    def test_expired_latest_shard_iterator_preserves_initial_seek_timestamp(self) -> None:
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        seen_codes: list[str] = []

        def save(ser: Any) -> None:
            seen_codes.append(ser.validated_data["code"])

        FakeStateSerializer = self.mock_state_serializer_drf(save)
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)

        # Record arrives after the LATEST iterator was created, before any record is fetched
        client.put_record(
            StreamName=TOPIC_STATES,
            Data=b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
            PartitionKey="NY",
        )

        raw_client = consumer.consumer.client
        real_get_records = raw_client.get_records
        expired_err = ClientError(
            {"Error": {"Code": "ExpiredIteratorException", "Message": "Iterator expired"}},
            "GetRecords",
        )
        calls = 0

        def get_records_expire_once(**kwargs: Any) -> Any:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise expired_err
            return real_get_records(**kwargs)

        with (
            patch.object(raw_client, "get_records", side_effect=get_records_expire_once),
            patch.object(
                raw_client,
                "get_shard_iterator",
                wraps=raw_client.get_shard_iterator,
            ) as get_iter_mock,
        ):
            consumer.run(iter_limit=1)

        self.assertEqual(calls, 2)
        get_iter_mock.assert_called_once_with(
            StreamName=TOPIC_STATES,
            ShardId="shardId-000000000000",
            ShardIteratorType="AT_TIMESTAMP",
            Timestamp=consumer.consumer.initial_seek_timestamps["shardId-000000000000"],
        )
        self.assertEqual(seen_codes, ["NY"])

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_expired_shard_iterator_refresh_client_error_skips_shard_and_recovers(self) -> None:
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)
        client.put_record(
            StreamName=TOPIC_STATES,
            Data=b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
            PartitionKey="NY",
        )

        seen_codes: list[str] = []

        def save(ser: Any) -> None:
            seen_codes.append(ser.validated_data["code"])

        FakeStateSerializer = self.mock_state_serializer_drf(save)
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)

        raw_client = consumer.consumer.client
        real_get_records = raw_client.get_records
        real_get_shard_iterator = raw_client.get_shard_iterator

        expired_err = ClientError(
            {"Error": {"Code": "ExpiredIteratorException", "Message": "Iterator expired"}},
            "GetRecords",
        )
        throttle_err = ClientError(
            {"Error": {"Code": "LimitExceededException", "Message": "Rate exceeded"}},
            "GetShardIterator",
        )

        get_records_calls = 0
        get_shard_iter_calls = 0

        def mock_get_records(**kwargs: Any) -> Any:
            nonlocal get_records_calls
            get_records_calls += 1
            if get_records_calls <= 2:
                raise expired_err
            return real_get_records(**kwargs)

        def mock_get_shard_iterator(**kwargs: Any) -> Any:
            nonlocal get_shard_iter_calls
            get_shard_iter_calls += 1
            if get_shard_iter_calls == 1:
                raise throttle_err
            return real_get_shard_iterator(**kwargs)

        with (
            patch.object(raw_client, "get_records", side_effect=mock_get_records),
            patch.object(raw_client, "get_shard_iterator", side_effect=mock_get_shard_iterator),
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            lag = consumer.consumer._load_next_page()
            self.assertEqual(lag, 0)
            self.assertEqual(get_shard_iter_calls, 1)
            self.assertEqual(len(consumer.consumer.shards), 1)
            sleep_mock.assert_called_once_with(5)

            consumer.run(iter_limit=1)

        self.assertEqual(seen_codes, ["NY"])

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_non_throttle_client_error_backs_off_once_and_keeps_shard(self) -> None:
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)
        raw_client = consumer.consumer.client

        # Non-throttle ClientError on get_records does not retry in a tight loop: sleeps once and skips shard
        access_denied = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "Access denied"}},
            "GetRecords",
        )
        with (
            patch.object(raw_client, "get_records", side_effect=access_denied) as get_records_mock,
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            consumer.run(iter_limit=1)
        self.assertEqual(get_records_mock.call_count, 1)
        sleep_mock.assert_called_once_with(5)
        self.assertEqual(len(consumer.consumer.shards), 1)
        self.assertEqual(len(consumer.consumer.shard_iters), 1)

        # ClientError during expired-iterator refresh also sleeps once, skips shard, and preserves state
        expired_err = ClientError(
            {"Error": {"Code": "ExpiredIteratorException", "Message": "Iterator expired"}},
            "GetRecords",
        )
        not_found = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Stream deleted"}},
            "GetShardIterator",
        )
        with (
            patch.object(raw_client, "get_records", side_effect=expired_err),
            patch.object(raw_client, "get_shard_iterator", side_effect=not_found) as refresh_mock,
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            consumer.run(iter_limit=1)
        self.assertEqual(refresh_mock.call_count, 1)
        sleep_mock.assert_called_once_with(5)
        self.assertEqual(len(consumer.consumer.shards), 1)
        self.assertEqual(len(consumer.consumer.shard_iters), 1)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_expired_shard_iterator_double_expiry_and_closed_shard_pool_update(self) -> None:
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)
        raw_client = consumer.consumer.client

        expired_err = ClientError(
            {"Error": {"Code": "ExpiredIteratorException", "Message": "Iterator expired"}},
            "GetRecords",
        )
        with (
            patch.object(raw_client, "get_records", side_effect=[expired_err, expired_err]),
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            self.assertEqual(consumer.consumer._load_next_page(), 0)
        sleep_mock.assert_not_called()
        self.assertEqual(len(consumer.consumer.shards), 1)
        self.assertEqual(len(consumer.consumer.shard_iters), 1)

        # NextShardIterator=None removes a closed shard from both shards and shard_iters
        real_resp = raw_client.get_records(
            ShardIterator=consumer.consumer.shard_iters["shardId-000000000000"],
            Limit=10,
        )
        closed_resp = {**real_resp, "NextShardIterator": None, "MillisBehindLatest": 0}
        with patch.object(raw_client, "get_records", return_value=closed_resp):
            consumer.run(iter_limit=1)
        self.assertEqual(self.serializers["state"].save.call_count, 1)
        self.assertEqual(len(consumer.consumer.shards), 0)
        self.assertEqual(len(consumer.consumer.shard_iters), 0)

    @override_settings(
        LOGPIPE={
            **LOGPIPE,
            "KINESIS_REGION": "us-east-1",
            "KINESIS_CONSUMER_KWARGS": {"region_name": "us-west-2"},
        }
    )
    @mock_aws
    def test_model_offset_store_uses_consumer_client_region(self) -> None:
        west_client = boto3.client("kinesis", region_name="us-west-2")
        west_client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)
        west_client.put_record(
            StreamName=TOPIC_STATES,
            Data=b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
            PartitionKey="NY",
        )

        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=1)

        offset = KinesisOffset.objects.get(stream=TOPIC_STATES, shard="shardId-000000000000")
        self.assertEqual(offset.region, "us-west-2")
        self.assertEqual(offset.sequence_number, "1")

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_multi_shard_consume(self):
        # Send a bunch of messages to a bunch of shards
        key = 1
        value = b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}'
        client = self.make_stream_with_record(str(key), value, shard_count=20)
        for i in range(100):
            key += 1
            client.put_record(StreamName=TOPIC_STATES, Data=value, PartitionKey=str(key))

        # Test the values sent to our serializer match the message
        test = {"i": 0}

        def save(ser):
            self.assertEqual(ser.validated_data["code"], "NY")
            self.assertEqual(ser.validated_data["name"], "New York")
            test["i"] += 1

        FakeStateSerializer = self.mock_state_serializer_drf(save)

        # Consume messages. Log should have 101 messages in it now.
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=2000)
        self.assertEqual(FakeStateSerializer.call_count, 101)
        self.assertEqual(test["i"], 101)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_missing_version_throws(self):
        self.make_stream_with_record("NY", b'json:{"message":{"code":"NY","name":"New York"}}')
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500, throw_errors=True)
        with self.assertRaises(InvalidMessageError):
            consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_missing_version_ignored(self):
        self.make_stream_with_record("NY", b'json:{"message":{"code":"NY","name":"New York"}}')
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_missing_message_throws(self):
        self.make_stream_with_record("NY", b'json:{"version":1}')
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500, throw_errors=True)
        with self.assertRaises(InvalidMessageError):
            consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_missing_message_ignored(self):
        self.make_stream_with_record("NY", b'json:{"version":1}')
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_unknown_version_throws(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":2,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500, throw_errors=True)
        consumer.register(FakeStateSerializer)
        with self.assertRaises(UnknownMessageVersionError):
            consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_unknown_version_ignored(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":2,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_invalid_message_throws(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NYC","name":"New York"},"version":1,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500, throw_errors=True)
        consumer.register(FakeStateSerializer)
        with self.assertRaises(ValidationError):
            consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 1)
        self.assertEqual(self.serializers["state"].save.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_invalid_message_throws_pydantic(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NYC","name":"New York"},"version":1,"type":"us-state"}',
        )
        save = MagicMock()
        FakeStateSerializer = self.mock_state_serializer_pydantic(save)
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500, throw_errors=True)
        consumer.register(FakeStateSerializer)
        with self.assertRaises(ValidationError):
            consumer.run(iter_limit=1)
        self.assertEqual(save.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_invalid_message_ignored(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NYC","name":"New York"},"version":1,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=1)
        self.assertEqual(FakeStateSerializer.call_count, 1)
        self.assertEqual(self.serializers["state"].save.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_invalid_message_ignored_pydantic(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NYC","name":"New York"},"version":1,"type":"us-state"}',
        )
        save = MagicMock()
        FakeStateSerializer = self.mock_state_serializer_pydantic(save)
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=1)
        self.assertEqual(save.call_count, 0)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_ignored_message_type_is_ignored(self):
        self.make_stream_with_record(
            "NY",
            b'json:{"message":{"code":"NY","name":"New York"},"version":1,"type":"us-state"}',
        )
        FakeStateSerializer = self.mock_state_serializer_drf()
        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.add_ignored_message_type("us-state")
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=1)
        # Even though message is valid, the serializer should never get called since message type is explicitly ignored.
        self.assertEqual(FakeStateSerializer.call_count, 0)
        self.assertTrue("state" not in self.serializers)

    def make_stream_with_record(self, key, value, shard_count=1):
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=shard_count)
        client.put_record(StreamName=TOPIC_STATES, Data=value, PartitionKey=key)
        return client
