FROM registry.gitlab.com/thelabnyc/python:3.13.1005@sha256:cbded9bab8ecbc35e8724fe4e7922515a81861d6c9f256f52ea161e33cccdfc3

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
