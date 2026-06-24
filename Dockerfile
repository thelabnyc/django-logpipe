FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:5dcaa64f66f018e87f6592ac2117af3017f9d703f363dd8923e82e094fc988bb

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
