FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3-pip git\
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /src/requirements.txt
COPY app /src/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]