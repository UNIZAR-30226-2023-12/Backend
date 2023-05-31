#!/bin/bash

./rm.sh

if docker images melodia/django:latest | grep -q melodia/django
then
    echo "La imagen docker de django está instalada en su equipo. Se va a utilizar la imagen encontrada para generar el contenedor."
else
    echo "No se ha encontrado la imagen docker de django. La imagen para generar el contenedor se va a crear a partir de los ficheros existentes."
    if [ -f django_image.tar ]
    then
        docker image load -i django_image.tar
    else
        ./build.sh
    fi
fi
docker compose up -d
