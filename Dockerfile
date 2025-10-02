FROM registry.gitlab.com/thelabnyc/python:3.13.983@sha256:430b61d298d0c1245c4ab7154fb70a26772530966e0c974cf3609fd8d3e475e2

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
