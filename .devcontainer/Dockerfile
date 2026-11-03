FROM mcr.microsoft.com/devcontainers/python:3.15-trixie

# convttf (build-fonts.sh) links against libfreetype.so.6
RUN apt-get update \
    && apt-get install -y --no-install-recommends libfreetype6 zip \
    && rm -rf /var/lib/apt/lists/*
