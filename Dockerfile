FROM registry.gitlab.com/thelabnyc/python:3.15@sha256:e8f93efa6a89cacc9dbe9cfff0cb0b7e0b596c5aeec9b23fedb5798b2e40a1fc

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
