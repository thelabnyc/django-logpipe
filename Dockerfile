FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:1562e9ace19290b1cefe14ed21abcb0773e2a2310c8ac0a58e18fd1001ea69a1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
