FROM registry.gitlab.com/thelabnyc/python:3.13.678@sha256:8b330520901706e453726582eb600ccf1e977268be1c6122456c1db06313c1ee

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
