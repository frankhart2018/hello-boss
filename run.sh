#!/bin/bash

HOST=${1:-0.0.0.0}
PORT=${2:-8002}

echo "Starting server at $HOST:$PORT"
echo "To change pass host as first argument and port as second argument\n\n"

uvicorn app.main:app --host $HOST --port $PORT