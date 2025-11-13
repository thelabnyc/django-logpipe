FROM registry.gitlab.com/thelabnyc/python:3.13.1086@sha256:ba6afe926a1e3f876cadde3752e7bb43ff5978deab7b9ee0bd22c4f822554dd6

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
