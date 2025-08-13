FROM registry.gitlab.com/thelabnyc/python:3.13.898@sha256:d4e85348498aa158051a6d59169a8ec86fc7caef972b5ef9eca0aaa0c608304f

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
