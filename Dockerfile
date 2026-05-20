FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:dcfb264c5af270ea52ae5b71fc84acd78cd3ac7f9b31de2e94eb56b9104c27c6

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
