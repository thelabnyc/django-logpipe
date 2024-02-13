# Release Notes

## 1.4.0

- Drop support for Python 3.10.
- Add support for Python 3.12.
- Add Python type annotations.
- Add support for using [Pydantic](https://docs.pydantic.dev/) models as an alternative to DRF serializers.

## 1.3.0

- Add PRODUCER_ID setting to aid in debugging which systems sent which messages, especially when interrogating logged messages.

## 1.2.0

- Add Python 3.10 and 3.11 to test suite.
- Add Django 4.0 and 4.1 to test suite.
- Drop Python 3.8 from test suite.
- Drop Django 2.2, 3.0, and 3.1 from test suite.
- Added missing DB migrations (though no actual DB changes exist).

## 1.1.0

- Add Python 3.9 to test suite
- Add Django 3.2 to test suite

## 1.0.0

- No changes.

## 0.3.2

- Fix compatibility issue with Django 3.0

## 0.3.1

- Internationalization

## 0.3.0

- In KinesisOffset model, track the AWS region for a stream. This allows a single database to subscribe to multiple streams in different regions, even it they have the same name.
- Improved logic for detecting the current AWS region.
- Add Django 2.1 to tox test suite.
- Add support for Python 3.7.
- Add support for python-kafka 1.4.4.

## 0.2.1

- More robustly handle exceptions thrown by a consumer serializer's `save()` method.
- Improve log messages and levels for invalid or unknown messages.
- Add new method: `logpipe.Consumer.add_ignored_message_type`, which allows the consumer to explicitly ignore specific message types silently. This helps to filter log noise (messages that a consumer really doesn't care about) from actual errors (messages a consumer is skipping, but should be processing).

## 0.2.0

- Added concept of message types.
- Added support for AWS Kinesis.

## 0.1.0

- Initial release.
