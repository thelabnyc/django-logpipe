FROM registry.gitlab.com/thelabnyc/python:3.13.932@sha256:ed7f592ca78a217aaecbd90d8ee1f7fd6d8e97c1f90d78899e01d92a664fff04

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
