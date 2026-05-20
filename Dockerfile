FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:882fdbdd3085b09adc7f0d9d73de2a172992d680982b05839eaf36ee9d7b4948

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
