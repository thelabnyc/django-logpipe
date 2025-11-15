FROM registry.gitlab.com/thelabnyc/python:3.13.1097@sha256:43ecc7c2173da19b4e14028fd8326d24cf3fbc6661b4892d53f37ea9f2ed2338

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
