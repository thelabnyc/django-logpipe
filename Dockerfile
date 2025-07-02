FROM registry.gitlab.com/thelabnyc/python:3.13.789@sha256:8653d069ee80c0d104143560eb826916ccaaa6f1a42640b180d4d67d8bcd09c9

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
