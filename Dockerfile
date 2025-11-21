FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:d078a5c10f1c071e227dd49725de0ee6518a023083aa76da259df45deb5a8c36

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
