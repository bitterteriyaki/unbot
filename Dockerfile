FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /bot
COPY requirements.txt /bot/requirements.txt

RUN pip install -r requirements.txt
COPY . /bot/
