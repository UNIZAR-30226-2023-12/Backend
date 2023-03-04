import redis


#########################################################################################
#
#
# FUNCIONES PARA GESTIONAR EL CREADO/MODIFICACION DE PLAYLISTS
#
#
#########################################################################################

# Funcion para crear una playlist
def crearPlaylist(r, id, nombre, usuario, idListaIDsCanciones, canciones, podcasts, publica):
    # Primero creo la playlist con sus datos
    r.hmset(id, {'nombre': nombre, 'usuario': usuario, 'idListaIDsCanciones': idListaIDsCanciones, 'publica': publica})

    # Creo la lista de canciones y podcasts
    r.sadd(idListaIDsCanciones, *canciones)
    r.sadd(idListaIDsCanciones, *podcasts)

# Funcion para cambiar el nombre de una playlist
def cambiarNombrePlaylist(r, id, nombre):
    r.hset(id, 'nombre', nombre)

# Funcion para cambiar el usuario de una playlist
def cambiarUsuarioPlaylist(r, id, usuario):
    r.hset(id, 'usuario', usuario)

# Funcion para cambiar el tipo de playlist (publica o privada)
def cambiarPublicaPlaylist(r, id, publica):
    r.hset(id, 'publica', publica)

# Funcion para añadir una o más canciones a una playlist
def anadirCancionPlaylist(r, idLista, idCanciones):
    # Primero obtengo la lista de canciones de la playlist
    idListaCan = r.hget(idLista, 'idListaIDsCanciones')

    # Añado las canciones a la lista
    r.sadd(idListaCan, *idCanciones)

# Funcion para añadir un o más podcasts a una playlist
def anadirPodcastPlaylist(r, idLista, idPodcasts):
    # Primero obtengo la lista de podcasts de la playlist
    idListaPod = r.hget(idLista, 'idListaIDsCanciones')

    # Añado los podcasts a la lista
    r.sadd(idListaPod, *idPodcasts)