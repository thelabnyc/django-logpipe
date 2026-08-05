FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:16b40eba79a434205439cd230ad5910508ef226f2c8f935caf5440563e35a0d1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
