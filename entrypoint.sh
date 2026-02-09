#!/bin/bash

set -e

celery -A Project worker --loglevel=info --concurrency=1 &

uvicorn Project.asgi:application --host 0.0.0.0 --port 8000