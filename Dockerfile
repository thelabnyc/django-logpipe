FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:04def26a15dd439dd2b2109b335ea0f7bb22c92ca0ffc7025ed504309f395ea8

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
