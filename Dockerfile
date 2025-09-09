FROM registry.gitlab.com/thelabnyc/python:3.13.942@sha256:423986ecd83a0e45e53b0a027de5d2ed21e49bea9a29ff00902d07185ae6a345

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
