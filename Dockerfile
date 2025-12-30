FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:c00ac3017c7dec33983899beb489d0ed9615861c9f61e86a2e8de65eca3bd3fc

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
