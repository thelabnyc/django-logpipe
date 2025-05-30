FROM registry.gitlab.com/thelabnyc/python:3.13.719@sha256:bb4407fb7895ec7ddcb2eaa23dda805fc368e50b47934904efc254196be7975e

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
