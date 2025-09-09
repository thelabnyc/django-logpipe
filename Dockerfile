FROM registry.gitlab.com/thelabnyc/python:3.13.938@sha256:e581b3407059fb97f64e549a4138b67a33bbf5cefdc86807728da4e83c4654f9

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
