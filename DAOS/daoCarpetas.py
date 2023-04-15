import redis
import Configuracion.constantesPrefijosClaves as constantes

def getIdContador(r):
    return constantes.PREFIJO_ID_CARPETA + ":" + r.incr(constantes.CLAVE_CONTADOR_CARPETAS)

def existeCarpeta(r, id):
    if(r.exists(id) == 0):
        return False
    return True

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
def setCarpeta(r, carpetaDic):
    id = carpetaDic[constantes.CLAVE_ID_CARPETA]
    del carpetaDic[constantes.CLAVE_ID_CARPETA]

    # Primero creo la carpeta con sus datos
    return r.hmset(id, carpetaDic)

# Funcion para cambiar el nombre de una carpeta
def cambiarNombreCarpeta(r, id, nombre):
    return r.hset(id, constantes.CLAVE_NOMBRE_CARPETA, nombre)

# Funcion para cambiar el tipo de carpeta (publica o privada)
def setPrivacidadCarpeta(r, id, privacidad):
    return r.hset(id, constantes.CLAVE_PRIVACIDAD_CARPETA, privacidad)

# Funcion para añadir una o más playlists a una carpeta
def anyadirListaCarpeta(r, idCarpeta, idListas):
    return r.sadd(constantes.CLAVE_LISTAS_CARPETA + ":" + idCarpeta, *idListas)

# Funcion para eliminar una o más playlists de una carpeta
def eliminarListaCarpeta(r, idCarpeta, idPlaylists):
    return r.srem(constantes.CLAVE_LISTAS_CARPETA + ":" + idCarpeta, *idPlaylists)

# Funcion para eliminar una carpeta
def eliminarCarpeta(r, id):
    # Elimino la carpeta
    r.delete(id)
    
    # Elimino la lista de playlists de la carpeta
    r.delete(constantes.CLAVE_LISTAS_CARPETA + ":" + id)
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE CARPETAS
#
#
#########################################################################################


# Funcion para obtener una carpeta
def getCarpeta(r, id):
    return r.hgetall(id)

# Funcion para obtener el nombre de una carpeta
def getNombreCarpeta(r, id):
    return r.hget(id, constantes.CLAVE_NOMBRE_CARPETA)

# Funcion para obtener el tipo de carpeta (publica o privada)
def getPrivacidadCarpeta(r, id):
    return r.hget(id, constantes.CLAVE_PRIVACIDAD_CARPETA)

# Funcion para obtener las playlists de una carpeta
def getListasCarpeta(r, id):
    stop = False
    iterador = 0
    playlistsCarpeta = []
    while not stop:
        scan = r.sscan(constantes.CLAVE_LISTAS_CARPETA + ":" + id, iterador, count=100)
        playlistsCarpeta.extend(scan[1])
        iterador = scan[0]
        if iterador == 0:
            stop = True
    
    return playlistsCarpeta