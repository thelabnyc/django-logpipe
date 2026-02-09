FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:255422c95f7119da37c0da3f2e7eb7662254d1db1130c96520b894de092109fa

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
