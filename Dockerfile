FROM registry.gitlab.com/thelabnyc/python:3.13.810@sha256:a1bdc5490a42db1600428af3ac25a0582f28bafb412179340234dc495ab12070

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
