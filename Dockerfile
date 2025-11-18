FROM registry.gitlab.com/thelabnyc/python:3.13.1114@sha256:24f145fd6740d8600a47b4b5cd45d335a325f3d8b2d6a74f67670c161c5ec943

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
