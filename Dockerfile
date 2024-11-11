from python:3.12.7-slim-bullseye

WORKDIR /app
RUN apt-get update && apt-get install -y etherwake

COPY main.py .
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt
CMD ["fastapi", "run"]
