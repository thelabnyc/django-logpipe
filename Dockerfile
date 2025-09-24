FROM registry.gitlab.com/thelabnyc/python:3.13.970@sha256:620114e732e448d14e809d37b28f77757ab22c2b2112aa2fb9cd8caf85dbc583

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
