FROM registry.gitlab.com/thelabnyc/python:3.15@sha256:a04134afa4cc0bbde93cf357c2a1ffc8683590054a5cf99e1fa3eb929bb4aaa5

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
