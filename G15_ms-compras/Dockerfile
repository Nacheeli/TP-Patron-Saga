FROM python:3.10-slim-bullseye

ENV FLASK_ENV=development \
    PYTHONUNBUFFERED=1 \
    PATH=$PATH:/home/flaskapp/.local/bin

RUN useradd --create-home --home-dir /home/flaskapp flaskapp
WORKDIR /home/flaskapp

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/flaskapp/

USER flaskapp

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]