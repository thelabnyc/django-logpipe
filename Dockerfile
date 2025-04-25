FROM registry.gitlab.com/thelabnyc/python:py313@sha256:ef829aa095beb081cf1c8c6868ef38644176b297b555144bce07bc9c3205038a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
