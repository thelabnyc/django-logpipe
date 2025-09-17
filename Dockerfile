FROM registry.gitlab.com/thelabnyc/python:3.13.961@sha256:2c96555191b14909c223e9767ae4f8bb420b3aab0c9452408279947340089c34

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
