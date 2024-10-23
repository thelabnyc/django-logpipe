# Installation

Install `django-logpipe` from pip.

```sh
pip install django-logpipe
```

Add `logpipe` to your installed apps.

```py
INSTALLED_APPS = [
    # …
    'logpipe',
    # …
]
```

Add connection settings to your `settings.py` file. If you're using Kafka, this will look like this:

```py
LOGPIPE = {
    # Required Settings
    'OFFSET_BACKEND': 'logpipe.backend.kafka.ModelOffsetStore',
    'CONSUMER_BACKEND': 'logpipe.backend.kafka.Consumer',
    'PRODUCER_BACKEND': 'logpipe.backend.kafka.Producer',
    'KAFKA_BOOTSTRAP_SERVERS': [
        'kafka:9092'
    ],
    'KAFKA_CONSUMER_KWARGS': {
        'group_id': 'django-logpipe',
    },

    # Optional Settings
    'KAFKA_SEND_TIMEOUT': 10,
    'KAFKA_MAX_SEND_RETRIES': 0,
    'KAFKA_KWARGS': {
        # Example for Confluent Cloud
        'security_protocol': 'SASL_SSL',
        'sasl_mechanism': 'PLAIN',
        'sasl_plain_username': '<api_key>',
        'sasl_plain_password': '<api_secret>',
        # …or for OVHCloud
        'security_protocol': 'SSL',
        'ssl_cafile': '<ca.pem or ca.certificate.pem>',
        'ssl_certfile': '<service.cert or access.certificate.pem>',
        'ssl_keyfile': '<service.key or access.key>',
    },
    'MIN_MESSAGE_LAG_MS': 0,
    'DEFAULT_FORMAT': 'json',
    'PRODUCER_ID': 'my-application-name',
}
```

If you're using AWS Kinesis instead of Kafka, it will look like this:

```py
LOGPIPE = {
    # Required Settings
    'OFFSET_BACKEND': 'logpipe.backend.kinesis.ModelOffsetStore',
    'CONSUMER_BACKEND': 'logpipe.backend.kinesis.Consumer',
    'PRODUCER_BACKEND': 'logpipe.backend.kinesis.Producer',

    # Optional Settings
    # 'KINESIS_REGION': 'us-east-1',
    # 'KINESIS_FETCH_LIMIT': 25,
    # 'KINESIS_SEQ_NUM_CACHE_SIZE': 1000,
    # 'MIN_MESSAGE_LAG_MS': 0,
    # 'DEFAULT_FORMAT': 'json',
    # 'PRODUCER_ID': 'my-application-name',
}
```

Run migrations. This will create the model used to store Kafka log position offsets.

```sh
python manage.py migrate logpipe
```
