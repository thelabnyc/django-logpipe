FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:5e79e7662259f4d0c0ccceebaf193d710e9cac99205f33ea347d0c180ce18fc5

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
