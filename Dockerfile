FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:7f1db4fb98fbf83156b8c586f9fe7879bceee4e210e353d34c67fd984d86910f

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
