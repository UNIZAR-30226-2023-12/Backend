#!/bin/bash

# copiar ficheros necesarios
cp ../../manage.py .
cp -r ../../backend_melodia/ .
cp -r ../../Configuracion/ .
cp -r ../../DAOS/ .
cp -r ../../frontApi/ .
cp -r ../../Usuarios/ .

# construir la imagen
docker build -t melodia/django:latest .

# eliminar las copias redundantes
rm -f manage.py
rm -rf ./backend_melodia/
rm -rf ./Configuracion/
rm -rf ./DAOS/
rm -rf ./frontApi/
rm -rf ./Usuarios/