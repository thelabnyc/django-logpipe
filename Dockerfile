FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:69e37e1668070251e454860ca363c094696f3f11ee803f577efdf04359abb9ee

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
