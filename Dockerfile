FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:edbd39af42a307b838bef85a01e78336c5d4b0e7e438989d3ca0e61b5dac5223

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
