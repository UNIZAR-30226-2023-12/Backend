#!/bin/bash

./cli.sh SET idUltimoAudio 0
./cli.sh SET contadorUsuarios 0
./cli.sh SET contadorListas 0
./cli.sh SET contadorNotificaciones 0
./cli.sh SET contadorCarpetas 

usrDefaultImage=$( base64 ../../Configuracion/defaultUserImage.png )
audioDefaultImage=$( base64 ../../Configuracion/defaultAudioImage.png )

redis-cli --user melodia --pass melodia_Proyecto_Software_Grupo_12 --raw SET defaultUserImage "$usrDefaultImage"
redis-cli --user melodia --pass melodia_Proyecto_Software_Grupo_12 --raw SET defaultAudioImage "$audioDefaultImage"

docker cp redis:/data/appendonlydir ./appendonlydir