#!/bin/bash

./cli.sh SET idUltimoAudio 0
./cli.sh SET contadorUsuarios 0
./cli.sh SET contadorListas 0
./cli.sh SET contadorNotificaciones 0
./cli.sh SET contadorCarpetas 0
./cli.sh SET defaultUserImage < cat ../../Configuracion/defaultUserImage.png

docker cp redis:/data/appendonlydir ./appendonlydir