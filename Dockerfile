FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:c2b946f4d8bfc284831caac2e394672174514e1177ad3db5b2772d07ba805d55

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
