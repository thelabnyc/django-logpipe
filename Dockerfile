FROM registry.gitlab.com/thelabnyc/python:3.13.923@sha256:32f25961da5a764b276e53f1828090ad71a5b5e12cc4baf5c4ab8fd8135ade5a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
