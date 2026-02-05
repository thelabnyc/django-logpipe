FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:1ec621a105849222b1eaa6f3d90d5bbb16fefdbb90befb77350a4424c164ca4c

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
