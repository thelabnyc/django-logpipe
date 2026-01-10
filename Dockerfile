FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:23b5db0beeb4e9aa1d9d04ade5f37146ae20687659c25b43b5a86f93e4cb96fc

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
