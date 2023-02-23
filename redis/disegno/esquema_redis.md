# ESQUEMA DE PERSISTENCIA DE DATOS EN REDIS

Versión 1.0

## ENTIDADES

* Canción

    Hash → Cancion:id_canción | nombre artista calidad fichero nº_reproducciones valoración_media generos

* Podcast

    Hash → Podcast:id_podcast | nombre artista calidad fichero nº_reproducciones valoración_media generos descripción

* Lista

    Hash → Lista:id_lista | nombre creador privada_o_publica reproducción_o_favoritos

* Usuario

    Hash → Usuario:email | alias contraseña es_artista es_administrador

* Carpeta

    Hash → Carpeta:id_carpeta | nombre creador

## RELACIONES

* Audio en Lista

    Set → AudiosDentroDeLista:id_lista | id_audio

* Lista en Carpeta

    Set → ListasDentroDeCarpeta: id_carpeta | id_lista

* Amigos

    Set → Amigos:email | email_amigos
