#!/bin/bash

if docker images melodia/redis:latest | grep -q melodia/redis; then
    echo "La imagen docker de redis está instalada en su equipo. Se va a utilizar la imagen encontrada para generar el contenedor."
else
    echo "No se ha encontrado la imagen docker de redis. La imagen para generar el contenedor se va a crear a partir de los ficheros existentes."
    docker image load -i redis_image.tar
fi

docker compose up -d
