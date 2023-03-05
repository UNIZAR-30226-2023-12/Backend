import redis


#########################################################################################
#
#
# FUNCIONES PARA GESTIONAR EL CREADO/MODIFICACION DE PLAYLISTS
# Una playlist tiene los siguientes posibles atributos:
#   - id (clave para el hash)
#   - nombre
#   - usuario
#   - idListaIDsCanciones
#   - publica
#
#
#########################################################################################

# Funcion para crear una playlist
def crearPlaylist(r, playlistDic, canciones, podcasts):
    # Primero creo la playlist con sus datos
    id = playlistDic['id']
    del playlistDic['id']

    r.hmset(id, playlistDic)

    # Creo la lista de canciones y podcasts
    r.sadd(playlistDic['idListaIDsCanciones'], *canciones)
    r.sadd(playlistDic['idListaIDsCanciones'], *podcasts)

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

# Funcion para eliminar una o más canciones de una playlist
def eliminarCancionPlaylist(r, idLista, idCanciones):
    # Primero obtengo la lista de canciones de la playlist
    idListaCan = r.hget(idLista, 'idListaIDsCanciones')

    # Elimino las canciones de la lista
    r.srem(idListaCan, *idCanciones)

# Funcion para eliminar un o más podcasts de una playlist
def eliminarPodcastPlaylist(r, idLista, idPodcasts):
    # Primero obtengo la lista de podcasts de la playlist
    idListaPod = r.hget(idLista, 'idListaIDsCanciones')

    # Elimino los podcasts de la lista
    r.srem(idListaPod, *idPodcasts)

# Funcion para eliminar una playlist
def eliminarPlaylist(r, id):
    # Primero obtengo la lista de canciones de la playlist
    idListaCan = r.hget(id, 'idListaIDsCanciones')

    # Elimino la playlist
    r.delete(id)

    # Elimino la lista de canciones de la playlist
    r.delete(idListaCan)

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE PLAYLISTS
#
#
#########################################################################################

# Funcion para obtener una playlist
def obtenerPlaylist(r, id):
    return r.hgetall(id)

# Funcion para obtener el nombre de una playlist
def obtenerNombrePlaylist(r, id):
    return r.hget(id, 'nombre')

# Funcion para obtener el usuario de una playlist
def obtenerUsuarioPlaylist(r, id):
    return r.hget(id, 'usuario')

# Funcion para obtener el tipo de playlist (publica o privada)
def obtenerPublicaPlaylist(r, id):
    return r.hget(id, 'publica')

# Funcion para obtener las canciones de una playlist
def obtenerCancionesPlaylist(r, id):
    # Primero obtengo la lista de canciones de la playlist
    idListaCan = r.hget(id, 'idListaIDsCanciones')

    # Devuelvo los miembros de la lista
    return r.smembers(idListaCan)

# Funcion para obtener los podcasts de una playlist
def obtenerPodcastsPlaylist(r, id):
    # Primero obtengo la lista de podcasts de la playlist
    idListaPod = r.hget(id, 'idListaIDsCanciones')

    # Devuelvo los miembros de la lista
    return r.smembers(idListaPod)

# Funcion para obtener el id de la lista de canciones de una playlist
def obtenerIDListaCancionesPlaylist(r, id):
    return r.hget(id, 'idListaIDsCanciones')

#########################################################################################
#
#
# FUNCIONES PARA CREAR/MODIFICAR CARPETAS
# Una carpeta tiene los siguientes posibles atributos:
#   - id (clave para el hash)
#   - nombre
#   - usuario
#   - idListaIDsPlaylist
#   - publica
#
#
#########################################################################################

# Funcion para crear una carpeta
def crearCarpeta(r, carpetaDic, playlists):
    id = carpetaDic['id']
    del carpetaDic['id']

    # Primero creo la carpeta con sus datos
    r.hmset(id, carpetaDic)

    # Creo la lista de playlists
    r.sadd(carpetaDic['idListaIDsPlaylist'], *playlists)

# Funcion para cambiar el nombre de una carpeta
def cambiarNombreCarpeta(r, id, nombre):
    r.hset(id, 'nombre', nombre)

# Funcion para cambiar el usuario de una carpeta
def cambiarUsuarioCarpeta(r, id, usuario):
    r.hset(id, 'usuario', usuario)

# Funcion para cambiar el tipo de carpeta (publica o privada)
def cambiarPublicaCarpeta(r, id, publica):
    r.hset(id, 'publica', publica)

# Funcion para añadir una o más playlists a una carpeta
def anadirPlaylistCarpeta(r, idCarpeta, idPlaylists):
    # Primero obtengo la lista de playlists de la carpeta
    idListaPlay = r.hget(idCarpeta, 'idListaIDsPlaylist')

    # Añado las playlists a la lista
    r.sadd(idListaPlay, *idPlaylists)

# Funcion para eliminar una o más playlists de una carpeta
def eliminarPlaylistCarpeta(r, idCarpeta, idPlaylists):
    # Primero obtengo la lista de playlists de la carpeta
    idListaPlay = r.hget(idCarpeta, 'idListaIDsPlaylist')

    # Elimino las playlists de la lista
    r.srem(idListaPlay, *idPlaylists)

# Funcion para eliminar una carpeta
def eliminarCarpeta(r, id):
    # Primero obtengo la lista de playlists de la carpeta
    idListaPlay = r.hget(id, 'idListaIDsPlaylist')

    # Elimino la carpeta
    r.delete(id)

    # Elimino la lista de playlists de la carpeta
    r.delete(idListaPlay)

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE CARPETAS
#
#
#########################################################################################

# Funcion para obtener una carpeta
def obtenerCarpeta(r, id):
    return r.hgetall(id)

# Funcion para obtener el nombre de una carpeta
def obtenerNombreCarpeta(r, id):
    return r.hget(id, 'nombre')

# Funcion para obtener el usuario de una carpeta
def obtenerUsuarioCarpeta(r, id):
    return r.hget(id, 'usuario')

# Funcion para obtener el tipo de carpeta (publica o privada)
def obtenerPublicaCarpeta(r, id):
    return r.hget(id, 'publica')

# Funcion para obtener las playlists de una carpeta
def obtenerPlaylistsCarpeta(r, id):
    # Primero obtengo la lista de playlists de la carpeta
    idListaPlay = r.hget(id, 'idListaIDsPlaylist')

    # Devuelvo los miembros de la lista
    return r.smembers(idListaPlay)

# Funcion para obtener el id de la lista de playlists de una carpeta
def obtenerIDListaPlaylistsCarpeta(r, id):
    return r.hget(id, 'idListaIDsPlaylist')