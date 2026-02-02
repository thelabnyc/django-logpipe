FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:1be853e6f27965f57ba0fc6bdc2651ecbc3bcb02becc38b983b6af363cbc39ed

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
