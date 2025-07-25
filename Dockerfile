FROM registry.gitlab.com/thelabnyc/python:3.13.868@sha256:9842728501a6def27787aa6b4e657baea930e0e56e7beaae0bd8aed205129bad

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
