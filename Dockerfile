FROM registry.gitlab.com/thelabnyc/python:3.13.947@sha256:d2726970dbfb36d7ff8ae613f6f2b544a99d07b100ed2347b9168b9bab583c9b

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
