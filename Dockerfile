FROM registry.gitlab.com/thelabnyc/python:3.13.707@sha256:379ebd0f299bf4cf64c5c0c829afebe3b622aae78f02fcc04d779488e330b8ff

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
