FROM registry.gitlab.com/thelabnyc/python:3.13.680@sha256:13b2ea1750ff14bb8366fa5aa843d38d22cdf66e7c27b77d80bae082732ae045

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
