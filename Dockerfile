FROM registry.gitlab.com/thelabnyc/python:3.13.763@sha256:c8fb927482806c90d82e48c4c3f8188803549b0f676f9d64fb1342604e7c4a66

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
