FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:91a9936eb357496d309cd159e18d91e223b6fc6e7b6b67d3d625747b1cf90858

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
