FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:8bca3aa0acae2855762d9cf8df651468bb855cfcdc700db9aad6c8923dcd2dd2

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
