FROM registry.gitlab.com/thelabnyc/python:3.13.955@sha256:25baf707a184f087e2d69968307b785548b0463446da41a4049d0c04d1adf2aa

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
