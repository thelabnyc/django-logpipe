FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:d5f5e272767535d07a13c8a817760e0c42f72e61df42c8378fddb89eedaccebc

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
