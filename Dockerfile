FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:8fe8a44cfb4a81b8e6706b7180c1c990f993c76e0736e509343ac8b3bafd6473

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
