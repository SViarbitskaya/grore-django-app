###########
# BUILDER #
###########

# pull official base image
FROM python:3.11.4-slim-buster as builder

# set work directory
WORKDIR /usr/src/grore

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

# lint
RUN pip install --upgrade pip
# RUN pip install flake8==6.0.0
COPY . /usr/src/grore/
# RUN flake8 --ignore=E501,F401 .

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/grore/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.11.4-slim-buster

# create directory for the app user
RUN mkdir -p /home/grore

# create the app user
RUN addgroup --system grore && adduser --system --group grore

# create the appropriate directories
ENV HOME=/home/grore
ENV APP_HOME=/home/grore/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/grore/wheels /wheels
COPY --from=builder /usr/src/grore/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint.sh
COPY ./scripts/docker/django/entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME
# RUN rm -Rf $APP_HOME/venv
# RUN python -v venv venv
# $APP_HOME/venv/bin/pip -r requirements.txt


# chown all the files to the app user
RUN chown -R grore:grore $APP_HOME

# change to the app user
USER grore

# run entrypoint.sh
ENTRYPOINT ["/home/grore/web/entrypoint.sh"]
