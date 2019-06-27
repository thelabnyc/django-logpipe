FROM python:3.7
ENV PYTHONUNBUFFERED 0

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/
RUN pip install -e .[development,msgpack,kafka,kinesis]

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
