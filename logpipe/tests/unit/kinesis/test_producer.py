from contextvars import copy_context
from unittest.mock import patch

from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    ParamValidationError,
    ReadTimeoutError,
)
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from moto import mock_aws
import boto3

from logpipe import Producer, PydanticProducer, reuse_producer
from logpipe.backend.kinesis import (
    DEFAULT_KINESIS_CONNECT_TIMEOUT,
    DEFAULT_KINESIS_MAX_ATTEMPTS,
    DEFAULT_KINESIS_READ_TIMEOUT,
)
from logpipe.tests.common import (
    TOPIC_STATES,
    State_Pydantic,
    StateModel,
    StateSerializer_DRF,
)

LOGPIPE = {
    "OFFSET_BACKEND": "logpipe.backend.kinesis.ModelOffsetStore",
    "PRODUCER_BACKEND": "logpipe.backend.kinesis.Producer",
    "CONSUMER_BACKEND": "logpipe.backend.kinesis.Consumer",
}


class DRFProducerTest(TestCase):
    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_normal_send(self):
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        producer = Producer(TOPIC_STATES, StateSerializer_DRF)

        ret = producer.send({"code": "NY", "name": "New York"})
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, "shardId-000000000000")
        self.assertEqual(ret.offset, "1")

        ret = producer.send({"code": "PA", "name": "Pennsylvania"})
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, "shardId-000000000000")
        self.assertEqual(ret.offset, "2")

        shard_iter = client.get_shard_iterator(
            StreamName=TOPIC_STATES,
            ShardId="shardId-000000000000",
            ShardIteratorType="TRIM_HORIZON",
        )["ShardIterator"]
        response = client.get_records(ShardIterator=shard_iter, Limit=100)

        self.assertEqual(response["Records"][0]["SequenceNumber"], "1")
        self.assertJSONEqual(
            response["Records"][0]["Data"].decode().replace("json:", ""),
            {
                "type": "us-state",
                "version": 1,
                "message": {
                    "code": "NY",
                    "name": "New York",
                },
            },
        )
        self.assertEqual(response["Records"][0]["PartitionKey"], "NY")

        self.assertEqual(response["Records"][1]["SequenceNumber"], "2")
        self.assertJSONEqual(
            response["Records"][1]["Data"].decode().replace("json:", ""),
            {
                "type": "us-state",
                "version": 1,
                "message": {
                    "code": "PA",
                    "name": "Pennsylvania",
                },
            },
        )
        self.assertEqual(response["Records"][1]["PartitionKey"], "PA")

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_object_send(self):
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        producer = Producer(TOPIC_STATES, StateSerializer_DRF)

        obj = StateModel(
            code="NY",
            name="New York",
        )
        ret = producer.send(obj)
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, "shardId-000000000000")
        self.assertEqual(ret.offset, "1")

        obj = StateModel(
            code="PA",
            name="Pennsylvania",
        )
        ret = producer.send(obj)
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, "shardId-000000000000")
        self.assertEqual(ret.offset, "2")

        shard_iter = client.get_shard_iterator(
            StreamName=TOPIC_STATES,
            ShardId="shardId-000000000000",
            ShardIteratorType="TRIM_HORIZON",
        )["ShardIterator"]
        response = client.get_records(ShardIterator=shard_iter, Limit=100)

        self.assertEqual(response["Records"][0]["SequenceNumber"], "1")
        self.assertJSONEqual(
            response["Records"][0]["Data"].decode().replace("json:", ""),
            {
                "type": "us-state",
                "version": 1,
                "message": {
                    "code": "NY",
                    "name": "New York",
                },
            },
        )
        self.assertEqual(response["Records"][0]["PartitionKey"], "NY")

        self.assertEqual(response["Records"][1]["SequenceNumber"], "2")
        self.assertJSONEqual(
            response["Records"][1]["Data"].decode().replace("json:", ""),
            {
                "type": "us-state",
                "version": 1,
                "message": {
                    "code": "PA",
                    "name": "Pennsylvania",
                },
            },
        )
        self.assertEqual(response["Records"][1]["PartitionKey"], "PA")

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_default_botocore_timeouts_and_retries(self) -> None:
        producer = Producer(TOPIC_STATES, StateSerializer_DRF)
        boto_config = producer.client.client.meta.config
        self.assertEqual(boto_config.connect_timeout, DEFAULT_KINESIS_CONNECT_TIMEOUT)
        self.assertEqual(boto_config.read_timeout, DEFAULT_KINESIS_READ_TIMEOUT)
        self.assertEqual(
            boto_config.retries,
            {"total_max_attempts": DEFAULT_KINESIS_MAX_ATTEMPTS, "mode": "standard"},
        )

    @override_settings(
        LOGPIPE={
            **LOGPIPE,
            "KINESIS_CONNECT_TIMEOUT": 3,
            "KINESIS_READ_TIMEOUT": 7,
            "KINESIS_MAX_ATTEMPTS": 4,
            "KINESIS_KWARGS": {
                "endpoint_url": "https://kinesis.us-east-1.amazonaws.com",
                "config": {
                    "user_agent_extra": "logpipe-shared",
                    "retries": {"mode": "adaptive"},
                },
            },
            "KINESIS_PRODUCER_KWARGS": {
                "region_name": "us-west-2",
                "config": Config(read_timeout=12),
            },
        }
    )
    @mock_aws
    def test_custom_timeout_and_producer_kwargs_override_defaults(self) -> None:
        producer = Producer(TOPIC_STATES, StateSerializer_DRF)
        boto_config = producer.client.client.meta.config
        self.assertEqual(boto_config.connect_timeout, 3)
        self.assertEqual(boto_config.read_timeout, 12)
        self.assertEqual(boto_config.user_agent_extra, "logpipe-shared")
        self.assertEqual(boto_config.retries, {"total_max_attempts": 4, "mode": "adaptive"})
        self.assertEqual(producer.client.client.meta.region_name, "us-west-2")

        with override_settings(
            LOGPIPE={
                **LOGPIPE,
                "KINESIS_KWARGS": {"config": "not-a-config"},
            }
        ):
            bad_producer = Producer(TOPIC_STATES, StateSerializer_DRF)
            with self.assertRaises(ImproperlyConfigured):
                _ = bad_producer.client.client

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_close_releases_client(self) -> None:
        producer = Producer(TOPIC_STATES, StateSerializer_DRF)
        client = producer.client.client
        with patch.object(client, "close", wraps=client.close) as close:
            with producer:
                pass
            producer.close()
        close.assert_called_once_with()
        self.assertIsNone(producer.client._client)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_reuse_producer_shares_backend_and_closes_on_exit(self) -> None:
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        with reuse_producer():
            p1 = PydanticProducer(TOPIC_STATES)
            p2 = Producer(TOPIC_STATES, StateSerializer_DRF)
            self.assertIs(p1.client, p2.client)
            raw_client = p1.client.client
            close_patcher = patch.object(raw_client, "close", wraps=raw_client.close)
            close = close_patcher.start()
            self.addCleanup(close_patcher.stop)

            # Inner `with PydanticProducer(...)` or `.close()` does not close the shared backend early
            with PydanticProducer(TOPIC_STATES) as p_ctx:
                self.assertIs(p1.client, p_ctx.client)
            p1.close()
            close.assert_not_called()

            with reuse_producer():
                p3 = PydanticProducer(TOPIC_STATES)
                self.assertIs(p1.client, p3.client)
                p1.send(State_Pydantic(code="NY", name="New York"))
                p2.send({"code": "PA", "name": "Pennsylvania"})
            # Inner re-entrant scope does not close the shared client early
            close.assert_not_called()

            child_ctx = copy_context()

        # Exiting the outer scope closes the shared client
        close.assert_called_once_with()
        self.assertIsNone(p1.client._client)

        p4 = PydanticProducer(TOPIC_STATES)
        self.assertIsNot(p1.client, p4.client)

        # A copied Context that outlives `reuse_producer()` does not hand out the closed backend
        p_child = child_ctx.run(PydanticProducer, TOPIC_STATES)
        self.assertIsNot(p1.client, p_child.client)

        # A scoped producer that sends again after its scope ended reopens a client it now owns and can close
        p1.send(State_Pydantic(code="NJ", name="New Jersey"))
        reopened_client = p1.client._client
        self.assertIsNotNone(reopened_client)
        self.assertIsNot(reopened_client, raw_client)
        with patch.object(reopened_client, "close", wraps=reopened_client.close) as reopened_close:
            p1.close()
        reopened_close.assert_called_once_with()
        self.assertIsNone(p1.client._client)

    @override_settings(LOGPIPE=LOGPIPE)
    @mock_aws
    def test_reuse_producer_isolates_close_errors_and_preserves_body_exception(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "body failure"), reuse_producer():
            p1 = PydanticProducer(TOPIC_STATES)
            with override_settings(LOGPIPE={**LOGPIPE, "PRODUCER_BACKEND": "logpipe.backend.dummy.Producer"}):
                p2 = PydanticProducer(TOPIC_STATES)
            close1_patcher = patch.object(p1.client, "close", side_effect=OSError("close 1 boom"))
            close2_patcher = patch.object(p2.client, "close")
            close1 = close1_patcher.start()
            close2 = close2_patcher.start()
            self.addCleanup(close1_patcher.stop)
            self.addCleanup(close2_patcher.stop)
            raise RuntimeError("body failure")
        close1.assert_called_once_with()
        close2.assert_called_once_with()

    @override_settings(LOGPIPE={**LOGPIPE, "KINESIS_MAX_SEND_RETRIES": 1})
    @mock_aws
    def test_send_and_retry_retries_client_errors_and_propagates_botocore_errors(self) -> None:
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        producer = PydanticProducer(TOPIC_STATES)
        raw_client = producer.client.client

        # Transport and non-transport BotoCoreError exceptions propagate directly from put_record
        # (botocore's retry handler already owns transport retries within put_record).
        for botocore_err in (
            ReadTimeoutError(endpoint_url="https://kinesis.us-east-1.amazonaws.com"),
            EndpointConnectionError(endpoint_url="https://kinesis.us-east-1.amazonaws.com"),
            ParamValidationError(report="invalid param"),
            NoCredentialsError(),
        ):
            with (
                patch.object(
                    raw_client,
                    "put_record",
                    side_effect=botocore_err,
                ) as botocore_err_mock,
                self.assertRaises(type(botocore_err)),
            ):
                producer.send(State_Pydantic(code="NY", name="New York"))
            self.assertEqual(botocore_err_mock.call_count, 1)

        # ClientError (e.g. ProvisionedThroughputExceededException) sleeps only between retries, not after final attempt
        with (
            patch.object(
                raw_client,
                "put_record",
                side_effect=ClientError(
                    {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "throttled"}},
                    "PutRecord",
                ),
            ) as throttle_mock,
            patch("logpipe.backend.kinesis.time.sleep") as sleep_mock,
        ):
            self.assertIsNone(producer.send(State_Pydantic(code="NY", name="New York")))
        self.assertEqual(throttle_mock.call_count, 2)
        sleep_mock.assert_called_once_with(5)
