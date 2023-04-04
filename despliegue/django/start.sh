#!/bin/bash

if docker images melodia/django:latest | grep -q melodia/django; then
    echo "La imagen docker de django está instalada en su equipo. Se va a utilizar la imagen encontrada para generar el contenedor."
else
    echo "No se ha encontrado la imagen docker de django. La imagen para generar el contenedor se va a crear a partir de los ficheros existentes."
    docker image load -i django_image.tar
fi
docker compose up -d
