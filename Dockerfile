FROM registry.gitlab.com/thelabnyc/python:3.13.812@sha256:7cb6fd74c3a16a6bb05e60fd3c1936baa4e3da9d54898fae20ebdd860c41de91

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
