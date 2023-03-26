AHORA MISMO EL CONTENEDOR DE DJANGO NO FUNCIONA

Ejecutar start.sh

Aunque el fichero docker-compose.yml está preparado para levantar un contenedor para redis y un contenedor para django, de momento el contenedor de django fallará.

Si lo queremos hacer a mano, PASOS A HACER PARA QUE FUNCIONE:

PRIMERO, ejecutar el script que se encarga de construir la imagen de django. Este es el paso que falla si hacemos docker compose up -d de golpe:

```[bash]
cd django && ./build.sh
```

Después, levantar los dos contenedores (asegurándose de que estamos en el directorio despliegue) con:

```[bash]
docker compose up -d
```