import redis
import Configuracion.constantesPrefijosClaves as constantesPrefijosClaves

def getIdContador(r):
    id = r.get(constantesPrefijosClaves.CLAVE_CONTADOR_CARPETAS)
    if(id == None):
        r.set(constantesPrefijosClaves.CLAVE_CONTADOR_CARPETAS, 0)
        id = 0
    pipe = r.pipeline()
    pipe.get(constantesPrefijosClaves.CLAVE_CONTADOR_CARPETAS)
    pipe.incr(constantesPrefijosClaves.CLAVE_CONTADOR_CARPETAS)
    id = pipe.execute()[0]
    return id

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
        print('Error: El nombre no puede estar vacío')
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
        print('Error: El usuario no puede estar vacío')
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

# Funcion para añadir una o más playlists a una carpeta
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
        
            # Añado las playlists a la lista
            r.sadd(idListaPlay, *idPlaylists)
    return 0

# Funcion para eliminar una o más playlists de una carpeta
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