FROM registry.gitlab.com/thelabnyc/python:3.13.800@sha256:386926768fd339f176561d92523fb4016c4fb5aec53bd4e0493c463e4080b618

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
