FROM registry.gitlab.com/thelabnyc/python:3.13.1073@sha256:fc57d03afe8305de9755798212a7f47ff16225f32bd62ac34ea51084b30c552a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
