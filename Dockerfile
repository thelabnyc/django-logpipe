FROM registry.gitlab.com/thelabnyc/python:3.13.860@sha256:ff95b4a51e864a87c37a2af6b61f4737071dc7cfab215040370f51637991b844

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
