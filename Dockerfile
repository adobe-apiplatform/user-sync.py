FROM python:3.9-slim as builder

RUN apt-get update && \
    apt-get install -y software-properties-common  \
    build-essential \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    pkg-config \
    libssl-dev \
    libdbus-1-dev \
    libdbus-glib-1-dev \
    python3-dbus \
    libffi-dev \
    libkrb5-dev

WORKDIR /app/user-sync.py

COPY . .

RUN pip install ./sign_client
RUN pip install external/okta-0.0.3.1-py2.py3-none-any.whl
RUN pip install -e .
RUN pip install -e .[test]
RUN pip install -e .[setup]
RUN make

FROM debian:bullseye-slim

COPY --from=builder /app/user-sync.py/dist/user-sync /usr/local/bin/user-sync

ENTRYPOINT [ "user-sync" ]
