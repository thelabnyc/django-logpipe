FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:486864e4aaf15ecd905acf8c6f28ce8659a135f430d99cb9e2d84de5673dcb02

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
