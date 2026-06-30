FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:7cb97eb739da0a5c29869fe63361427ce17abcf1059e4e9b83ae6142e83ede7a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
