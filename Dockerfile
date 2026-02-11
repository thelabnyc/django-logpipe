FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:2b16f6f5435bc0a80fda3fbf0a342bbad7ea52657a995eacdcf6726b21efc564

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
