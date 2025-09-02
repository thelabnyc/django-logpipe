FROM registry.gitlab.com/thelabnyc/python:3.13.927@sha256:3559d259f6908d4eda3fb1fe8ad5fdd5c9e98077ea171ce00fbddbac78e9f1e6

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
