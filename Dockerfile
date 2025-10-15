FROM registry.gitlab.com/thelabnyc/python:3.13.1007@sha256:6c31c6dbf68bdb47ba54034782e6dfcab6a09688a5567a67db59918ffa64244b

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
