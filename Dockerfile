FROM registry.gitlab.com/thelabnyc/python:3.13.1031@sha256:8c05203745ccf12bd27d8ef92222a28a08ab6c417f684c0447cc01d282f0079d

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
