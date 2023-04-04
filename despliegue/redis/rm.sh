#!/bin/bash

./stop.sh
docker rm redis
docker rmi melodia/redis
