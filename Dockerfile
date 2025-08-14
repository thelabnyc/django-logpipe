FROM registry.gitlab.com/thelabnyc/python:3.13.902@sha256:bfd590d6602e7040089cdf64f5eaa0b376e6ee2a1b556a62db2392f92bc3ebf8

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
