FROM registry.gitlab.com/thelabnyc/python:3.13.1100@sha256:67eabf2e2dda0e5da618d3b6d9c20cde25cd37fed7183aaee3c9f37ee9696f97

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
