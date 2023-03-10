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
        pipeLine = r.pipeline()
        for cancion in canciones:
            # Utilizo un pipeline para hacer las comprobaciones de forma mas eficiente
            pipeLine.exists(cancion)
        for podcast in podcasts:
            pipeLine.exists(podcast)
        resultados = pipeLine.execute()
        # Compruebo que los resultados de las comprobaciones son correctos
        for resultado in resultados:
            if not resultado:
                print('Error: Alguna de las canciones o podcasts no existen')
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

# Funcion para a??adir una o m??s canciones a una playlist
def anadirCancionPlaylist(r, idLista, idCanciones):
    # Compruebo que existe el set de canciones de la playlist y que las canciones existen
    if not r.exists(idLista):
        print('Error: La lista de canciones con ' + idLista + ' no existe')
        return -1
    elif len(idCanciones) == 0:
        print('Error: No se han introducido canciones para a??adir a la playlist')
        return -1
    else:
        anadir = True
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for cancion in idCanciones:
            pipeLine.exists(cancion)

        resultados = pipeLine.execute()

        for resultado in resultados:
            if not resultado:
                print('Error: Alguna de las canciones no existe')
                anadir = False
                return -1

        if anadir:
            # Primero obtengo la lista de canciones de la playlist
            idListaCan = r.hget(idLista, 'idListaIDsCanciones')

            # A??ado las canciones a la lista
            r.sadd(idListaCan, *idCanciones)
    return 0

# Funcion para a??adir un o m??s podcasts a una playlist
def anadirPodcastPlaylist(r, idLista, idPodcasts):
    # Compruebo que existe el set de podcasts de la playlist y que los podcasts existen
    if not r.exists(idLista):
        print('Error: La lista de podcasts con ' + idLista + ' no existe')
        return -1
    elif len(idPodcasts) == 0:
        print('Error: No se han introducido podcasts para a??adir a la playlist')
        return -1
    else:
        anadir = True
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for podcast in idPodcasts:
            pipeLine.exists(podcast)

        resultados = pipeLine.execute()

        for resultado in resultados:
            if not resultado:
                print('Error: Alguno de los podcasts no existe')
                anadir = False
                return -1

        if anadir:
            # Primero obtengo la lista de podcasts de la playlist
            idListaPod = r.hget(idLista, 'idListaIDsCanciones')
    
            # A??ado los podcasts a la lista
            r.sadd(idListaPod, *idPodcasts)
    return 0

# Funcion para eliminar una o m??s canciones de una playlist
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
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for cancion in idCanciones:
            pipeLine.exists(cancion)

        resultados = pipeLine.execute()

        for resultado in resultados:
            if not resultado:
                print('Error: Alguna de las canciones no existe')
                eliminar = False
                return -1
                    
        if eliminar:
            # Primero obtengo la lista de canciones de la playlist
            idListaCan = r.hget(idLista, 'idListaIDsCanciones')

            # Elimino las canciones de la lista
            r.srem(idListaCan, *idCanciones)
    return 0

# Funcion para eliminar un o m??s podcasts de una playlist
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
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for podcast in idPodcasts:
            pipeLine.exists(podcast)

        resultados = pipeLine.execute()


        for resultado in resultados:
            if not resultado:
                print('Error: Alguno de los podcasts no existe')
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
    
        # Devuelvo los miembros de la lista utilizando sscan
        stop = False
        iterador = 0
        cancionesPlaylist = []
        while not stop:
            scan = r.sscan(idListaCan, iterador, count=100)
            cancionesPlaylist.extend(scan[1])
            iterador = scan[0]
            if iterador == 0:
                stop = True

        return cancionesPlaylist

# Funcion para obtener los podcasts de una playlist
def obtenerPodcastsPlaylist(r, id):
    # Compruebo que la playlist existe
    if not r.exists(id):
        print('Error: La playlist ' + id + ' no existe')
        return -1
    else:
        # Primero obtengo la lista de podcasts de la playlist
        idListaPod = r.hget(id, 'idListaIDsCanciones')

        # Devuelvo los miembros de la lista utilizando sscan
        stop = False
        iterador = 0
        podcastsPlaylist = []
        while not stop:
            scan = r.sscan(idListaPod, iterador, count=100)
            podcastsPlaylist.extend(scan[1])
            iterador = scan[0]
            if iterador == 0:
                stop = True
        
        return podcastsPlaylist

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
    # Compruebo que la carpeta tiene todos los atributos necesarios y que playlists es una lista no vacia
    if 'id' not in carpetaDic or 'nombre' not in carpetaDic or 'usuario' not in carpetaDic or 'publica' not in carpetaDic or 'idListaIDsPlaylist' not in carpetaDic:
        print('Error: No se han introducido todos los atributos necesarios para crear la carpeta')
        return -1
    elif len(playlists) == 0:
        print('Error: No se han introducido playlists para crear la carpeta')
        return -1
    else:
        crear = True
        # Compruebo que las playlists existen
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for playlist in playlists:
            pipeLine.exists(playlist)

        resultados = pipeLine.execute()

        for resultado in resultados:
            if not resultado:
                print('Error: Alguna de las playlists no existe')
                crear = False
                return -1

        if crear:
            id = carpetaDic['id']
            del carpetaDic['id']

            # Primero creo la carpeta con sus datos
            r.hmset(id, carpetaDic)

            # Creo la lista de playlists
            r.sadd(carpetaDic['idListaIDsPlaylist'], *playlists)
    return 0

# Funcion para cambiar el nombre de una carpeta
def cambiarNombreCarpeta(r, id, nombre):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    elif nombre == '':
        print('Error: El nombre no puede estar vac??o')
        return -1
    else:
        r.hset(id, 'nombre', nombre)
    return 0

# Funcion para cambiar el usuario de una carpeta
def cambiarUsuarioCarpeta(r, id, usuario):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    elif usuario == '':
        print('Error: El usuario no puede estar vac??o')
        return -1
    else:
        r.hset(id, 'usuario', usuario)
    return 0

# Funcion para cambiar el tipo de carpeta (publica o privada)
def cambiarPublicaCarpeta(r, id, publica):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    elif publica != 'True' and publica != 'False':
        print('Error: El tipo de carpeta debe ser True o False')
        return -1
    else:
        r.hset(id, 'publica', publica)
    return 0

# Funcion para a??adir una o m??s playlists a una carpeta
def anadirPlaylistCarpeta(r, idCarpeta, idPlaylists):
    # Compruebo que la carpeta existe
    if not r.exists(idCarpeta):
        print('Error: La carpeta ' + idCarpeta + ' no existe')
        return -1
    else:
        crear = True
        # Compruebo que las playlists existen
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for playlist in idPlaylists:
            pipeLine.exists(playlist)

        resultados = pipeLine.execute()

        for resultado in resultados:
            if not resultado:
                print('Error: Alguna de las playlists no existe')
                crear = False
                return -1

        if crear:
            # Primero obtengo la lista de playlists de la carpeta
            idListaPlay = r.hget(idCarpeta, 'idListaIDsPlaylist')
        
            # A??ado las playlists a la lista
            r.sadd(idListaPlay, *idPlaylists)
    return 0

# Funcion para eliminar una o m??s playlists de una carpeta
def eliminarPlaylistCarpeta(r, idCarpeta, idPlaylists):
    # Compruebo que la carpeta existe
    if not r.exists(idCarpeta):
        print('Error: La carpeta ' + idCarpeta + ' no existe')
        return -1
    else:
        crear = True
        # Compruebo que las playlists existen
        # Uso pipeline para hacer las comprobaciones de forma mas eficiente
        pipeLine = r.pipeline()

        for playlist in idPlaylists:
            pipeLine.exists(playlist)

        resultados = pipeLine.execute()

        for resultado in resultados:
            if not resultado:
                print('Error: Alguna de las playlists no existe')
                crear = False
                return -1
        
        if crear:
            # Primero obtengo la lista de playlists de la carpeta
            idListaPlay = r.hget(idCarpeta, 'idListaIDsPlaylist')
        
            # Elimino las playlists de la lista
            r.srem(idListaPlay, *idPlaylists)
    return 0

# Funcion para eliminar una carpeta
def eliminarCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:    
        # Primero obtengo la lista de playlists de la carpeta
        idListaPlay = r.hget(id, 'idListaIDsPlaylist')
    
        # Elimino la carpeta
        r.delete(id)
    
        # Elimino la lista de playlists de la carpeta
        r.delete(idListaPlay)
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE CARPETAS
#
#
#########################################################################################


# Funcion para obtener una carpeta
def obtenerCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:
        return r.hgetall(id)

# Funcion para obtener el nombre de una carpeta
def obtenerNombreCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'nombre')

# Funcion para obtener el usuario de una carpeta
def obtenerUsuarioCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'usuario')

# Funcion para obtener el tipo de carpeta (publica o privada)
def obtenerPublicaCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'publica')

# Funcion para obtener las playlists de una carpeta
def obtenerPlaylistsCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:
        # Primero obtengo la lista de playlists de la carpeta
        idListaPlay = r.hget(id, 'idListaIDsPlaylist')

        # Devuelvo los miembros de la lista utilizando sscan
        stop = False
        iterador = 0
        playlistsCarpeta = []
        while not stop:
            scan = r.sscan(idListaPlay, iterador, count=100)
            playlistsCarpeta.extend(scan[1])
            iterador = scan[0]
            if iterador == 0:
                stop = True
    
        return playlistsCarpeta

# Funcion para obtener el id de la lista de playlists de una carpeta
def obtenerIDListaPlaylistsCarpeta(r, id):
    # Compruebo que la carpeta existe
    if not r.exists(id):
        print('Error: La carpeta ' + id + ' no existe')
        return -1
    else:
        return r.hget(id, 'idListaIDsPlaylist')