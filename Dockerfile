FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:e2ac4f67885cdc31c2602ff500eb2574c5d847c9b44e73c796dc7b31a8a3f98a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
