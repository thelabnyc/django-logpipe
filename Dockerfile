FROM registry.gitlab.com/thelabnyc/python:3.13.1013@sha256:c4d38b461dc8c4fd164026353ef05202a7f1abe26582b6307f3be4a221e3b18b

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
