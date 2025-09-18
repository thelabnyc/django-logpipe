FROM registry.gitlab.com/thelabnyc/python:3.13.963@sha256:b9ccc26976f21618a01f30aefb783b88202c4720ea69c7d526984a0ca6d44ad7

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
