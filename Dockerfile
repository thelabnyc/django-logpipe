FROM registry.gitlab.com/thelabnyc/python:3.15@sha256:f193363cee93a158a846145943f9fdf8082da4d4debfebefe646d5eaa339df52

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
