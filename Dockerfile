FROM registry.gitlab.com/thelabnyc/python:3.13.766@sha256:281d5d17fa4c1b41c70ec718cb8991c32730d36ccbbb817601254e648c498b04

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
