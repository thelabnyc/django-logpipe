FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:d0e7e3895e1e3c269cb56687664513a51dae0b86c22b1524c6d5332327bb8c6d

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
