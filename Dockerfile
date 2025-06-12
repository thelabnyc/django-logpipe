FROM registry.gitlab.com/thelabnyc/python:3.13.741@sha256:c80419f2ec5c116b0a82c59798b10e7686691a8c334e0dc0cf72d8c06b3dec5b

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
