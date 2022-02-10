FROM python:latest

WORKDIR /src/user-sync.py

COPY . .

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    build-essential && \
    python3-dev && \
    python3-pip && \
    python3-virtualenv && \
    pkg-config && \
    libssl-dev && \
    libdbus-1-dev && \
    libdbus-glib-1-dev && \
    python-dbus && \
    libffi-dev && \
    libkrb5-dev
