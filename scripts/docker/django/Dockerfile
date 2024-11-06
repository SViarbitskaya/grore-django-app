# pull official base image
FROM python:3.11.4-slim-buster AS builder
 
ARG APP_DJANGO_ROOT

# set work directory
WORKDIR $APP_DJANGO_ROOT
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc netcat
# Verify essential directories
# RUN mkdir -p $DJANGO_STATIC_ROOT
# RUN mkdir -p $DJANGO_MEDIA_ROOT
# RUN mkdir -p $APP_CACHE_ROOT
