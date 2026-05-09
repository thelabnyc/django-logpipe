FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:893af2934aa1eaac54659703091c91d96b15aaf6df20b6cd0bf3d3bec1ffe335

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
