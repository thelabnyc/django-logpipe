from django.apps import apps
from lru import LRU
from .. import settings
from . import RecordMetadata, Record, get_offset_backend
import boto3
import collections
import logging
import time

logger = logging.getLogger(__name__)


class KinesisBase(object):
    _client = None

    @property
    def client(self):
        if not self._client:
            kwargs = self._get_client_config()
            self._client = boto3.client('kinesis', **kwargs)
        return self._client


    def _get_client_config(self):
        region = settings.get('KINESIS_REGION', 'us-east-1')
        return {
            'region_name': region,
        }



class ModelOffsetStore(object):
    def commit(self, consumer, message):
        KinesisOffset = apps.get_model(app_label='logpipe', model_name='KinesisOffset')
        logger.debug('Commit offset "%s" for stream "%s", shard "%s" to %s' % (
            message.offset, message.topic, message.partition, self.__class__.__name__))
        obj, created = KinesisOffset.objects.get_or_create(
            stream=message.topic,
            shard=message.partition)
        obj.sequence_number = message.offset
        obj.save()


    def seek(self, consumer, stream, shard):
        KinesisOffset = apps.get_model(app_label='logpipe', model_name='KinesisOffset')
        try:
            obj = KinesisOffset.objects.get(stream=stream, shard=shard)
            logger.debug('Seeking to offset "%s" on stream "%s", partition "%s"' % (obj.sequence_number, stream, shard))
            consumer.seek_to_sequence_number(shard, obj.sequence_number)
        except KinesisOffset.DoesNotExist:
            logger.debug('Seeking to beginning of stream "%s", partition "%s"' % (stream, shard))
            consumer.seek_to_sequence_number(shard, None)



class Consumer(KinesisBase):
    def __init__(self, topic_name, **kwargs):
        self.topic_name = topic_name
        self.client_kwargs = kwargs

        self.shards = collections.deque()
        self.records = collections.deque()
        self.shard_iters = {}

        shards = self._list_shard_ids()
        logger.debug('Found {} kinesis shards.'.format(len(shards)))
        backend = get_offset_backend()
        for shard in shards:
            self.shards.append(shard)
            backend.seek(self, self.topic_name, shard)


    def seek_to_sequence_number(self, shard, sequence_number=None):
        if sequence_number is None:
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType='TRIM_HORIZON')
        else:
            resp = self.client.get_shard_iterator(
                StreamName=self.topic_name,
                ShardId=shard,
                ShardIteratorType='AFTER_SEQUENCE_NUMBER',
                StartingSequenceNumber=sequence_number)
        self.shard_iters[shard] = resp['ShardIterator']


    def __iter__(self):
        return self


    def __next__(self):
        # Try and load records
        i = 0
        while len(self.records) <= 0 and i <= len(self.shards):
            self._load_next_page()
            i += 1

        # If we've tried all the shards and still don't have any records, stop iteration
        if len(self.records) == 0:
            raise StopIteration()

        # Return the left most record in the queue
        return self.records.popleft()


    def _load_next_page(self):
        # Load a page from the left-most shard in the queue
        try:
            shard = self.shards.popleft()
        except IndexError:
            return

        # Get the next shard iterator for the shard
        shard_iter = self.shard_iters.pop(shard, None)
        if not shard_iter:
            return

        # Fetch the records from Kinesis
        logger.debug('Loading page of records from {}.{}'.format(self.topic_name, shard))
        fetch_limit = settings.get('KINESIS_FETCH_LIMIT', 25)
        response = self.client.get_records(ShardIterator=shard_iter, Limit=fetch_limit)

        # Save the shard iterator for next time we need to get records from this shard
        self.shard_iters[shard] = response['NextShardIterator']

        # Add the records page into the queue
        timestamp = (time.time() * 1000) - response.get('MillisBehindLatest', 0)
        for r in response['Records']:
            record = Record(
                topic=self.topic_name,
                partition=shard,
                offset=r['SequenceNumber'],
                timestamp=timestamp,
                key=r['PartitionKey'],
                value=r['Data'])
            self.records.append(record)

        # Add the shard back to the right of the queue
        self.shards.append(shard)


    def _list_shard_ids(self):
        resp = self.client.describe_stream(StreamName=self.topic_name)
        return [shard['ShardId'] for shard in resp['StreamDescription']['Shards']]


    def _get_shard_iter(self, shard_id):
        resp = self.client.get_shard_iterator(
            StreamName=self.topic_name,
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON')
        return resp['ShardIterator']



class Producer(KinesisBase):
    _last_sequence_numbers = LRU(settings.get('KINESIS_SEQ_NUM_CACHE_SIZE', 1000))

    def send(self, topic_name, key, value):
        kwargs = {
            'StreamName': topic_name,
            'Data': value,
            'PartitionKey': key,
        }

        if topic_name not in self._last_sequence_numbers:
            self._last_sequence_numbers[topic_name] = {}
        last_seq_num = self._last_sequence_numbers[topic_name].get(key)
        if last_seq_num:
            kwargs['SequenceNumberForOrdering'] = last_seq_num

        metadata = self.client.put_record(**kwargs)

        shard_id = metadata['ShardId']
        seq_num = str(metadata['SequenceNumber'])
        self._last_sequence_numbers[topic_name][key] = seq_num

        return RecordMetadata(
            topic=topic_name,
            partition=shard_id,
            offset=seq_num)
