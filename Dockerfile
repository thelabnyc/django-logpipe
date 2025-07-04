FROM registry.gitlab.com/thelabnyc/python:3.13.806@sha256:690f97069802e24129be617896344a08068819418beb2735e01a8af2607bde71

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
