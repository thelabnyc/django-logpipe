FROM registry.gitlab.com/thelabnyc/python:3.13.936@sha256:65301677f0373728f5bd94e9c82a8e637fa4c2ec2ef3d23887dcabf8546b8a32

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
