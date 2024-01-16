FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y procps
RUN apt-get install -y build-essential libssl-dev

WORKDIR /ebook_moim/ebookFinder

COPY . /ebook_moim/ebookFinder

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN mkdir /var/log/gunicorn && touch /var/log/gunicorn/access.log && touch /var/log/gunicorn/error.log
