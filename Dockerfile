FROM registry.gitlab.com/thelabnyc/python:3.13.849@sha256:4a4aab38f1288807497850915a6aa83f9a32dd1da52c2ce381eabfa37202b891

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
