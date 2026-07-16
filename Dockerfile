FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:d93001af56ffab1af3ee736f303a504feae8c2937f5f78e50e9bfc7b2140292a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
