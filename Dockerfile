FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:7905ebab6491a567240c1780aa60583b0ec5ccb2334ab4ac5e61f7809699344a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
