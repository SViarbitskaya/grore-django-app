# pull official base image
FROM python:3.11.4-slim-buster AS builder
 
ARG APP_DJANGO_ROOT
ARG APP_SYS_USER
ARG APP_SYS_GROUP
ARG SYS_UID
ARG SYS_GID

# set work directory
WORKDIR $APP_DJANGO_ROOT
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install system dependencies
RUN apt-get update && apt-get install -y netcat sudo

RUN addgroup --system --gid $SYS_GID $APP_SYS_GROUP && adduser --system --uid $SYS_UID --group $APP_SYS_USER



# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

USER $SYS_UID