#!/bin/bash

if test $# -eq 0
then
    redis-cli --user melodia --pass melodia_Proyecto_Software_Grupo_12
else
    cadena=$1
    for i in "${@:2}"
    do
        cadena=$(echo "$cadena" "$i")
    done
    echo $cadena
    redis-cli --user melodia --pass melodia_Proyecto_Software_Grupo_12 --raw $cadena
fi
