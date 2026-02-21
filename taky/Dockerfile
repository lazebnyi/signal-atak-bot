FROM python:3.11-slim

RUN pip install --no-cache-dir 'taky==0.10' 'setuptools<81'

WORKDIR /data

EXPOSE 8089

ENTRYPOINT ["taky", "-c", "/data/taky.conf"]
