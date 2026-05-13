FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:a93eafa41356cc710b2e258d84ec050db838f52f465e105b8b30fb27c36094f9

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
