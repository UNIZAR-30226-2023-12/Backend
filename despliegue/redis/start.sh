#!/bin/bash

docker build -t melodia/redis:latest .
docker compose up -d
./populate.sh
