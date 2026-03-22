FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:02179604a284d1843f76e4c9994e2bbeef8c9e60c6807cd8f4616b1b7f186e36

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
