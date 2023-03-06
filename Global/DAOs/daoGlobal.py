#########################################################################################
#
#
# MODULO DAO PARA GESTIONAR LAS PLAYLISTS Y CARPETAS
# Este modulo contiene las funciones para crear, modificar y obtener datos de playlists y
# carpetas con el tratamiento de errores correspondiente.
#
#
#########################################################################################

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
    # Compruebo que las canciones y podcasts existen y que playlistDic contiene los atributos necesarios
    if 'id' not in playlistDic or 'nombre' not in playlistDic or 'usuario' not in playlistDic or 'idListaIDsCanciones' not in playlistDic or 'publica' not in playlistDic:
        print('Error: No se han introducido todos los atributos necesarios para crear la playlist')
        return -1
    elif len(canciones) == 0 and len(podcasts) == 0:
        print('Error: No se han introducido canciones ni podcasts para crear la playlist')
        return -1
    else:
        # Compruebo que las canciones y podcasts existen
        crear = True
        for cancion in canciones:
            if not r.exists(cancion):
                print('Error: La cancion ' + cancion + ' no existe')
                crear = False
                return -1
        for podcast in podcasts:
            if not r.exists(podcast):
                print('Error: El podcast ' + podcast + ' no existe')
                crear = False
                return -1

        if crear:
            # Primero creo la playlist con sus datos
            id = playlistDic['id']
            del playlistDic['id']
        
            r.hmset(id, playlistDic)
        
            # Creo la lista de canciones y podcasts
            r.sadd(playlistDic['idListaIDsCanciones'], *canciones)
            r.sadd(playlistDic['idListaIDsCanciones'], *podcasts)
    return 0

# Funcion para cambiar el nombre de una playlist
def cambiarNombrePlaylist(r, id, nombre):
    # Compruebo que la playlist existe y que el nombre no esta vacio
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    elif nombre == '':
        print('Error: El nombre no puede estar vacio')
        return -1
    else:
        r.hset(id, 'nombre', nombre)
    return 0

# Funcion para cambiar el usuario de una playlist
def cambiarUsuarioPlaylist(r, id, usuario):
    # Compruebo que la playlist existe y que el usuario no esta vacio
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    elif usuario == '':
        print('Error: El usuario no puede estar vacio')
        return -1
    else:
        r.hset(id, 'usuario', usuario)
    return 0

# Funcion para cambiar el tipo de playlist (publica o privada)
def cambiarPublicaPlaylist(r, id, publica):
    # Compruebo que la playlist existe y que el tipo de playlist es correcto
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    elif publica != 'True' and publica != 'False':
        print('Error: El tipo de playlist no es correcto, puede ser True o False')
        return -1
    else:
        r.hset(id, 'publica', publica)
    return 0

# Funcion para añadir una o más canciones a una playlist
def anadirCancionPlaylist(r, idLista, idCanciones):
    # Compruebo que existe el set de canciones de la playlist y que las canciones existen
    if not r.exists(idLista):
        print('Error: La lista de canciones con ' + idLista + ' no existe')
        return -1
    elif len(idCanciones) == 0:
        print('Error: No se han introducido canciones para añadir a la playlist')
        return -1
    else:
        anadir = True
        for cancion in idCanciones:
            if not r.exists(cancion):
                print('Error: La cancion ' + cancion + ' no existe')
                anadir = False
                return -1
            
        if anadir:
            # Primero obtengo la lista de canciones de la playlist
            idListaCan = r.hget(idLista, 'idListaIDsCanciones')

            # Añado las canciones a la lista
            r.sadd(idListaCan, *idCanciones)
    return 0

# Funcion para añadir un o más podcasts a una playlist
def anadirPodcastPlaylist(r, idLista, idPodcasts):
    # Compruebo que existe el set de podcasts de la playlist y que los podcasts existen
    if not r.exists(idLista):
        print('Error: La lista de podcasts con ' + idLista + ' no existe')
        return -1
    elif len(idPodcasts) == 0:
        print('Error: No se han introducido podcasts para añadir a la playlist')
        return -1
    else:
        anadir = True
        for podcast in idPodcasts:
            if not r.exists(podcast):
                print('Error: El podcast ' + podcast + ' no existe')
                anadir = False
                return -1
            
        if anadir:
            # Primero obtengo la lista de podcasts de la playlist
            idListaPod = r.hget(idLista, 'idListaIDsCanciones')
    
            # Añado los podcasts a la lista
            r.sadd(idListaPod, *idPodcasts)
    return 0

# Funcion para eliminar una o más canciones de una playlist
def eliminarCancionPlaylist(r, idLista, idCanciones):
    # Compruebo que existe el set de canciones de la playlist y que las canciones existen
    if not r.exists(idLista):
        print('Error: La lista de canciones con ' + idLista + ' no existe')
        return -1
    elif len(idCanciones) == 0:
        print('Error: No se han introducido canciones para eliminar de la playlist')
        return -1
    else:
        eliminar = True
        for cancion in idCanciones:
            if not r.exists(cancion):
                print('Error: La cancion ' + cancion + ' no existe')
                eliminar = False
                return -1
            
        if eliminar:
            # Primero obtengo la lista de canciones de la playlist
            idListaCan = r.hget(idLista, 'idListaIDsCanciones')

            # Elimino las canciones de la lista
            r.srem(idListaCan, *idCanciones)
    return 0

# Funcion para eliminar un o más podcasts de una playlist
def eliminarPodcastPlaylist(r, idLista, idPodcasts):
    # Compruebo que existe el set de podcasts de la playlist y que los podcasts existen
    if not r.exists(idLista):
        print('Error: La lista de podcasts con ' + idLista + ' no existe')
        return -1
    elif len(idPodcasts) == 0:
        print('Error: No se han introducido podcasts para eliminar de la playlist')
        return -1
    else:
        eliminar = True
        for podcast in idPodcasts:
            if not r.exists(podcast):
                print('Error: El podcast ' + podcast + ' no existe')
                eliminar = False
                return -1
            
        if eliminar:
            # Primero obtengo la lista de podcasts de la playlist
            idListaPod = r.hget(idLista, 'idListaIDsCanciones')

            # Elimino los podcasts de la lista
            r.srem(idListaPod, *idPodcasts)
    return 0

# Funcion para eliminar una playlist
def eliminarPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        # Primero obtengo la lista de canciones de la playlist
        idListaCan = r.hget(id, 'idListaIDsCanciones')

        # Elimino la playlist
        r.delete(id)

        # Elimino la lista de canciones de la playlist
        r.delete(idListaCan)
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE PLAYLISTS
#
#
#########################################################################################

# Funcion para obtener una playlist
def obtenerPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        return r.hgetall(id)

# Funcion para obtener el nombre de una playlist
def obtenerNombrePlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'nombre')

# Funcion para obtener el usuario de una playlist
def obtenerUsuarioPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'usuario')

# Funcion para obtener el tipo de playlist (publica o privada)
def obtenerPublicaPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'publica')

# Funcion para obtener las canciones de una playlist
def obtenerCancionesPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        # Primero obtengo la lista de canciones de la playlist
        idListaCan = r.hget(id, 'idListaIDsCanciones')
    
        # Devuelvo los miembros de la lista
        return r.smembers(idListaCan)

# Funcion para obtener los podcasts de una playlist
def obtenerPodcastsPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        # Primero obtengo la lista de podcasts de la playlist
        idListaPod = r.hget(id, 'idListaIDsCanciones')

        # Devuelvo los miembros de la lista
        return r.smembers(idListaPod)

# Funcion para obtener el id de la lista de canciones de una playlist
def obtenerIDListaCancionesPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
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