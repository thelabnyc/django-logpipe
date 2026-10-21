FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:832e3a7a95ae5f4cfc0d80b05e5765a8a8e2620c5b640c7cc095115caf9de532

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
