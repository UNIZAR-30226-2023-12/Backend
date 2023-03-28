import redis
import Configuracion.constantesPrefijosClaves as constantesPrefijosClaves

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
    

def anyadirLista(r, id, idLista):
    if(r.exists(id) == 0 or r.exists(idLista) == 0):
        return -1
    r.sadd(constantesPrefijosClaves.CLAVE_LISTAS + id, idLista)
    return 0

def eliminarLista(r, id, idLista):
    if(r.exists(id) == 0 or r.exists(idLista) == 0):
        return -1
    r.srem(constantesPrefijosClaves.CLAVE_LISTAS + id, idLista)
    return 0

def obtenerListas(r, id):
    if(r.exists(id) == 0):
        return -1
    parar = False
    cursor = 0
    listas = []

    while(parar == False):
        scan = r.sscan(constantesPrefijosClaves.CLAVE_LISTAS + id, cursor, count=100)
        cursor = scan[0]
        listas.extend(scan[1])
        if(cursor == 0):
            parar = True
    return listas  