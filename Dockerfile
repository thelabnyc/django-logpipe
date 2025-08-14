FROM registry.gitlab.com/thelabnyc/python:3.13.911@sha256:17b8e6c64b407ce1eb7a22be7f7aa5cf7a7c596da41e51c1a1a77211043e3925

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
