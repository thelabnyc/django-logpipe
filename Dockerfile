FROM registry.gitlab.com/thelabnyc/python:3.13.887@sha256:522524239c63ec7c35cba1fe38ff6a42c0abe202da0f5f6bfcfdc859e858e72c

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
