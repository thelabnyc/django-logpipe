FROM registry.gitlab.com/thelabnyc/python:3.13.702@sha256:1596e3db776aa4b6194e71ecc714bc2c94d1334611ebef78c1af83fd370b0723

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
