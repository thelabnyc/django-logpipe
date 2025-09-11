FROM registry.gitlab.com/thelabnyc/python:3.13.949@sha256:57ac1937867781a0c86be6ef8ae19cad30ace929dbf0a0d1bde58d1235965f89

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
