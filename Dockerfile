FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:97c3ad06b404e5d01640d29eac9f62935339b02976dfd25026f6fc263e929754

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
