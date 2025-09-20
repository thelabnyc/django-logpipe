FROM registry.gitlab.com/thelabnyc/python:3.13.965@sha256:244775433ac89edef5aa38d729a3e625b51fe8cb198d7e77b6f58fcd65e17560

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
