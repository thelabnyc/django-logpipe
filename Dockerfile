FROM registry.gitlab.com/thelabnyc/python:3.13.757@sha256:f0a88813fb9c8b39aabc536c441f6c4f334dbf9828168e59a8c291c5a8cd2731

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
