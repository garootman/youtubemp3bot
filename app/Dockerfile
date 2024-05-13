# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# install ffmpeg
RUN sudo apt-get install ffmpeg

# Add the current directory contents into the container at /app
ADD ./app /app

# Arguments are: OPENAI_TOKEN,  POSTGRES_URL, REDIS_PASSWORD
ARG OPENAI_TOKEN
ARG POSTGRES_URL
ARG REDIS_PASSWORD

# Set arg as environment variable
ENV OPENAI_TOKEN=$OPENAI_TOKEN
ENV POSTGRES_URL=$POSTGRES_URL
ENV REDIS_PASSWORD=$REDIS_PASSWORD

# Copy pomidorlib into the temporary image
COPY ./pomidorlib ./pomidorlib

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r /app/requirements.txt

# Install pomidorlib
RUN pip install -e ./pomidorlib

# tests!

# RUN pip install pytest
# RUN pytest 
# /app/tests

RUN apt-get update && apt-get install -y supervisor
COPY ./app_worker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf


# Run supervisord when the container launches
# CMD celery -A worker worker --loglevel=info
# WORKDIR /app/src
# CMD celery -A worker worker --loglevel=info
# CMD celery -A pomidorlib.worker worker --loglevel=info
CMD ["/usr/bin/supervisord"]
