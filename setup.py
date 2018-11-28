#!/usr/bin/env python
from setuptools import setup, find_packages, Distribution
import codecs
import os.path

# Make sure versiontag exists before going any further
Distribution().fetch_build_eggs('versiontag>=1.2.0')

from versiontag import get_version, cache_git_tag  # NOQA


packages = find_packages('src')

install_requires = [
    'Django>=1.11',
    'djangorestframework>=3.3.3',
    'lru-dict>=1.1.6',
]

extras_require = {
    'development': [
        'flake8>=3.3.0',
        'moto>=1.3.6,<1.3.7',
        'psycopg2cffi>=2.7.7',
        'tox>=2.7.0',
        'versiontag>=1.2.0',
    ],
    'kafka': [
        'kafka-python>=1.3.3',
    ],
    'kinesis': [
        'boto3>=1.4.4',
    ],
    'msgpack': [
        'msgpack-python>=0.4.8',
    ],
}



def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()


cache_git_tag()

setup(
    name='django-logpipe',
    description="Move data around between Python services using Kafka and/or AWS Kinesis and Django Rest Framework serializers.",
    version=get_version(pypi=True),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    author='Craig Weber',
    author_email='crgwbr@gmail.com',
    url='https://gitlab.com/thelabnyc/django-logpipe',
    license='ISC',
    package_dir={'': 'src'},
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
)
