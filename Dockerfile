FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:049a47032e5f01095aa0adf05b3f98fde454c1420685c816c3f4fd7ca832c1a6

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
