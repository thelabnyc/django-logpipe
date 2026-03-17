FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:f8ea2f563e8ea239e312a24794deaef769c4ee649ef511166cbe18ed95e26b5b

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
