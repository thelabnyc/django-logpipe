FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:e4956329574204f38b13d58aa9fb94ff4bf753237f724d5c43311a9de81873b6

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
