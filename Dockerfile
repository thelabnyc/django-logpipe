FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:b2a76c73d46bdb5bd8e50c51541236d0b062cfe36b0fb4ce682eba551a9e2f4e

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
