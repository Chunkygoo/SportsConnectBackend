FROM python:3.9-slim-buster

WORKDIR /usr/src

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get -y install \
    netcat gcc postgresql python3-pip git\
    && apt-get clean

RUN pip3 install --upgrade pip
COPY ./requirements.txt /usr/src/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/

CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app