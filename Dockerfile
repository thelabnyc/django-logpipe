FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:7d5e109bb4042efc7418b423c029585d511ac9acf4c75475df40db2ea9caf1ef

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
