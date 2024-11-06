# pull official base image
FROM python:3.11.4-slim-buster AS builder
 
ARG APP_DJANGO_ROOT
ARG DOCKER_USER
ARG DOCKER_GROUP
ARG DOCKER_UID
ARG DOCKER_GID

# set work directory
WORKDIR $APP_DJANGO_ROOT
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install system dependencies
RUN apt-get update && apt-get install -y netcat sudo

RUN addgroup --system --gid $DOCKER_GID $DOCKER_GROUP && adduser --system --uid $DOCKER_UID --group $DOCKER_USER

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

USER $DOCKER_UID