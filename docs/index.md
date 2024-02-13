# Welcome

[![](https://gitlab.com/thelabnyc/django-logpipe/badges/master/build.svg)](https://gitlab.com/thelabnyc/django-logpipe/commits/master)
[![](https://img.shields.io/pypi/l/django-logpipe.svg)](https://pypi.python.org/pypi/)
[![](https://badge.fury.io/py/django-logpipe.svg)](https://pypi.python.org/pypi/django-logpipe)
[![](https://img.shields.io/pypi/format/django-logpipe.svg)](https://pypi.python.org/pypi/django-logpipe)

Django-logpipe is a library that serves as a universal pipe for moving data around between Django applications and services. It supports serialization by means of [Django REST Framework][drf] and/or [Pydantic][pydantic], and supports using either [Apache Kafka][kafka]] or [Amazon Kinesis][kinesis] as the underlying data stream.

[drf]: http://www.django-rest-framework.org/
[pydantic]: https://docs.pydantic.dev/
[kafka]: https://kafka.apache.org/
[kinesis]: https://aws.amazon.com/kinesis/

To get started, continue to
