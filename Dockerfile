FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:0734df6eb93f45e426d5e308f61fb725d7b61ce04bce4ea572e0d826f9a9b01a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
