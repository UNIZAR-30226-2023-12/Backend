#!/bin/bash

docker build -t melodia/redis:latest .
docker image save melodia/redis:latest -o redis_image.tar