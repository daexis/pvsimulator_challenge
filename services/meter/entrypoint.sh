#!/bin/sh
echo "Waiting for RabbitMQ..."
while ! nc -z rabbitmq 5672; do
  sleep 0.1
done
echo "PostgreSQL started"
python -m meter