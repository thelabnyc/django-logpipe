FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:f1cf13a97a409df3de9b8d92a16636c7c0e8364458c95a82ccf29fcae95367fd

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
