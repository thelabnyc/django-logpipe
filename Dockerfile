FROM registry.gitlab.com/thelabnyc/python:3.15@sha256:489ff9c9e067787afcea3b4e2b344e2e8c507109a8362132bf28d6c442c5495c

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
