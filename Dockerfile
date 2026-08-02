FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:0fa951451b63f5bffd9e7e87396c3d8c256e345ae20f0f86b90ea3c7cbb0bad1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
