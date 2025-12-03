FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:71a092cc050bcfb3e795237c18521e964240331355ef059637a6a37b6bfffc3e

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
