FROM registry.gitlab.com/thelabnyc/python:3.13.696@sha256:1249af72b7409f00444105358dcba7bf94a6522f0db56470be86861f1d39c4b1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
