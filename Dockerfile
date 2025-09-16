FROM registry.gitlab.com/thelabnyc/python:3.13.957@sha256:db0566fc8c17a188cd079238813ae6df4010c7fa586f4fefcfa8c4bd34c0acfb

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
