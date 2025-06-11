FROM registry.gitlab.com/thelabnyc/python:3.13.739@sha256:c07abc9ab41783bc7731753e4c703a398163d0bb2b5f41001cf4ca61cd7ed119

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
