FROM registry.gitlab.com/thelabnyc/python:3.13.1076@sha256:5f4eeaa01f98078d63ca24118ec05e808050da96cc8a4d488b7e72cc301684ca

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
