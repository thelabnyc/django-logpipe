FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:235a2ecc28a9852fd55e582cb8142c94d11064d622bb98b64e75544871ed4366

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
