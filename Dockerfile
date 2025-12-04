FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:ddb71bc5cd982178418dc0186804796b0780b552d815ed5213bd520110b35103

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
