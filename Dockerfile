FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:a6afcc896aef58163c689a1a9df85eee9d0afeada446c641ca1e318770b1041f

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
