FROM registry.gitlab.com/thelabnyc/python:3.13.721@sha256:477cef5334457395e749045ac56d7e8c6ef3c46c52d31f987f3e8371ca56a472

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
