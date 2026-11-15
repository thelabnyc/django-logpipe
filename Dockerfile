FROM registry.gitlab.com/thelabnyc/python:3.15@sha256:f2be5893268aeaa0d74235d8861c16e1f5c85d8443a39cd06f8a73e9108a1d81

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
