FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:89144d9eefcfe1c3cc6866223c7de64ac824b1478f219a8e57a8e949c3765e86

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
