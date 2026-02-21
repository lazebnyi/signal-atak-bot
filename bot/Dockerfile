FROM python:3.12-slim

WORKDIR /app

COPY main.py ./
COPY core/ ./core/
COPY services/ ./services/

ENTRYPOINT ["python", "main.py"]
