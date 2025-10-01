FROM registry.gitlab.com/thelabnyc/python:3.13.978@sha256:71703915e944ea7f01de89cbd2e58d514aed38dbbfbdc3fc6ca9da3c57bcb096

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
