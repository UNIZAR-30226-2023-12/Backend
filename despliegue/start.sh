#!/bin/bash

cd django && ./build.sh
cd ..
docker compose up -d