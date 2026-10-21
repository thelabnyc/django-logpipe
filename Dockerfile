FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:9a9f865840d4ce0ddbc177555d64cadc13b51b3d51908a502a386c24aaef18dc

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
