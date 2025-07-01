FROM registry.gitlab.com/thelabnyc/python:3.13.787@sha256:ed39d4a272ff1189b9caa342cdf26b89221b318aa572ac3ec5ba2aaff6436349

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
