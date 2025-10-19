FROM registry.gitlab.com/thelabnyc/python:3.13.1022@sha256:d2e5f1ec28286ce197e4940616cbf6416cf03c39418ea2a590c61a4471059cb3

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
