FROM registry.gitlab.com/thelabnyc/python:3.13.826@sha256:26de8aad748da74ff4390fdbde3e04da0109f9275a0cbce1ea05ffdaedb6a719

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
