#!/bin/bash

./cli.sh SET idUltimoAudio 0
./cli.sh SET contadorUsuarios 0
./cli.sh SET contadorListas 0
./cli.sh SET contadorNotificaciones 0
./cli.sh SET contadorCarpetas 0
cat ../../Configuracion/defaultUserImage.png | redis-cli --user melodia --pass melodia_Proyecto_Software_Grupo_12 -x SET defaultUserImage 
cat ../../Configuracion/defaultAudioImage.png | redis-cli --user melodia --pass melodia_Proyecto_Software_Grupo_12 -x SET defaultAudioImage 
docker cp redis:/data/appendonlydir ./appendonlydir