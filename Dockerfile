FROM registry.gitlab.com/thelabnyc/python:3.13.1052@sha256:aaec4c649afd817c6a2d8b492c7cb0d7fdd4f416ec9494d9ed451333cabcb4e0

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
