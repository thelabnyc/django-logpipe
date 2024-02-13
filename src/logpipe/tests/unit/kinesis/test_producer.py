from django.test import TestCase, override_settings
from moto import mock_kinesis
import boto3

from logpipe import Producer
from logpipe.tests.common import TOPIC_STATES, StateModel, StateSerializer

LOGPIPE = {
    "OFFSET_BACKEND": "logpipe.backend.kinesis.ModelOffsetStore",
    "PRODUCER_BACKEND": "logpipe.backend.kinesis.Producer",
    "CONSUMER_BACKEND": "logpipe.backend.kinesis.Consumer",
}


class ProducerTest(TestCase):
    @override_settings(LOGPIPE=LOGPIPE)
    @mock_kinesis
    def test_normal_send(self):
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        producer = Producer(TOPIC_STATES, StateSerializer)

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
    @mock_kinesis
    def test_object_send(self):
        client = boto3.client("kinesis", region_name="us-east-1")
        client.create_stream(StreamName=TOPIC_STATES, ShardCount=1)

        producer = Producer(TOPIC_STATES, StateSerializer)

        obj = StateModel()
        obj.code = "NY"
        obj.name = "New York"
        ret = producer.send(obj)
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, "shardId-000000000000")
        self.assertEqual(ret.offset, "1")

        obj = StateModel()
        obj.code = "PA"
        obj.name = "Pennsylvania"
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
