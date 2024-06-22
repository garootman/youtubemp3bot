#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' ../.env | xargs)

# Build the Docker image for bot
docker build -t mytgbot \
  --build-arg POSTGRES_URL=$POSTGRES_URL \
  --build-arg REDIS_URL=$REDIS_URL \
  --build-arg REDIS_PASSWORD=$REDIS_PASSWORD \
  --build-arg TG_TOKEN=$TG_TOKEN \
  --build-arg ADMIN_ID=$ADMIN_ID \
  --build-arg PROXY_TOKEN=$PROXY_TOKEN \
  --build-arg ENV=$ENV \
  --build-arg GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --build-arg PAY_LINK=$PAY_LINK \
  -f Dockerfile_tgbot ..

# Build the Docker image for worker
docker build -t mytgbot \
  --build-arg POSTGRES_URL=$POSTGRES_URL \
  --build-arg REDIS_URL=$REDIS_URL \
  --build-arg REDIS_PASSWORD=$REDIS_PASSWORD \
  --build-arg TG_TOKEN=$TG_TOKEN \
  --build-arg ADMIN_ID=$ADMIN_ID \
  --build-arg PROXY_TOKEN=$PROXY_TOKEN \
  --build-arg ENV=$ENV \
  --build-arg GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --build-arg PAY_LINK=$PAY_LINK \
  -f Dockerfile_worker ..