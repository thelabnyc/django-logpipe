FROM registry.gitlab.com/thelabnyc/python:3.13.967@sha256:3cdf2dc0c597f964cd31cbb6a8549307d4c33b5e3e2e13bace82c685ae64dd4e

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
