FROM registry.gitlab.com/thelabnyc/python:3.13.881@sha256:b42f98e7ab38e4d3e7dd2aed74ba35b225011c108e0f20a85720d7b43925be54

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
