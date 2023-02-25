# ESQUEMA DE PERSISTENCIA DE DATOS EN REDIS

Versión 1.1

## ENTIDADES

* Canción

    Hash → Cancion:id_canción | nombre calidad fichero nº_reproducciones valoración_media generos

* Podcast

    Hash → Podcast:id_podcast | nombre calidad fichero nº_reproducciones valoración_media generos descripción

* Lista

    Hash → Lista:id_lista | nombre privada_o_publica reproducción_o_favoritos_o_ranking

* Usuario

    Hash → Usuario:email | alias contraseña es_artista es_administrador

* Carpeta
    
    Hash → Carpeta:id_carpeta | nombre creador


## RELACIONES

* forma parte de (Audio en Lista)

    Set → AudiosDentroDeLista:id_lista | id_audio

* compone (Lista en Carpeta)

    Set → ListasDentroDeCarpeta: id_carpeta | id_lista

* Amigos

    Set → Amigos:email | email_amigos

* suscrito a

    Set → Suscrito a:email_usuario_suscrito | email_artista_seguido

