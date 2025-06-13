FROM registry.gitlab.com/thelabnyc/python:3.13.747@sha256:673d555237af80b3e915332a464ed7b15af47504532a1fcbce01b3ab34165fec

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
