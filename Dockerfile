FROM registry.gitlab.com/thelabnyc/python:3.13.890@sha256:be420bd1e759744a9a0495a17845cfa8ce8b32f4914a0a6dcf840a9b02f679b2

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
