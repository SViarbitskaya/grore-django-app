# pull official base image
FROM python:3.11.4-slim-buster AS builder
 
ARG APP_DJANGO_ROOT
ARG APP_DJANGO_USER_USER
ARG APP_DJANGO_USER_GROUP
ARG APP_DJANGO_USER_UID
ARG APP_DJANGO_USER_GID

# set work directory
WORKDIR $APP_DJANGO_ROOT
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install system dependencies
RUN apt-get update && apt-get install -y netcat sudo

RUN addgroup --system --gid $APP_DJANGO_USER_GID $APP_DJANGO_USER_GROUP && adduser --system --uid $APP_DJANGO_USER_UID --group $APP_DJANGO_USER_USER

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

USER $APP_DJANGO_USER_UID