FROM registry.gitlab.com/thelabnyc/python:3.13.1009@sha256:6985a43a5fd1bc8b3045245b8e3b22c7586685dba4ea85b531c746698e342e07

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
