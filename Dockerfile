FROM registry.gitlab.com/thelabnyc/python:3.13.843@sha256:1a45ed66203c29a8d32d195ab446fc951893cf262bfae7344684e7baa335dbe6

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
