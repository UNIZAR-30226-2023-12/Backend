import redis
import Configuracion.constantesPrefijosClaves as constantes


listaClaves = [constantes.CLAVE_ID_LISTA, constantes.CLAVE_NOMBRE_LISTA, 
               constantes.CLAVE_PRIVACIDAD_LISTA, constantes.CLAVE_TIPO_LISTA]

def getIdContador(r):
    id = r.get(constantes.CLAVE_CONTADOR_LISTAS)
    if(id == None):
        r.set(constantes.CLAVE_CONTADOR_LISTAS, 0)
        id = 0
    pipe = r.pipeline()
    pipe.get(constantes.CLAVE_CONTADOR_LISTAS)
    pipe.incr(constantes.CLAVE_CONTADOR_LISTAS)
    id = pipe.execute()[0]
    return id

def existeLista(r, id):
    if(r.exists(id) == 0):
        return False
    return True

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
def setLista(r, listaDiccionario):
    id = listaDiccionario[constantes.CLAVE_ID_LISTA]
    del listaDiccionario[constantes.CLAVE_ID_LISTA]    
    return r.hmset(id, listaDiccionario)

# Funcion para cambiar el nombre de una playlist
def setNombreLista(r, idLista, nombre):
    return r.hset(idLista, constantes.CLAVE_NOMBRE_LISTA, nombre)   

# Funcion para cambiar el tipo de playlist (publica o privada)
def setPrivacidadLista(r, idLista, privacidad):
    return r.hset(idLista, constantes.CLAVE_PRIVACIDAD_LISTA, privacidad)
# Funcion para cambiar el tipo de playlist (reproduccion o favoritos o ranking) 
def setTipoLista(r, idLista, tipo):
    return r.hset(idLista, constantes.CLAVE_TIPO_LISTA, tipo)

# Funcion para añadir una o más canciones a una playlist
def anyadirAudioLista(r, idLista, idAudio):
    return r.sadd(constantes.CLAVE_AUDIOS + ":" + idLista, *idAudio)

# Funcion para eliminar una o más canciones de una playlist
def eliminarAudioLista(r, idLista, idAudio):
    return r.srem(constantes.CLAVE_AUDIOS + ":" + idLista, *idAudio)

# Funcion para eliminar una playlist
def eliminarLista(r, id):
    # Elimino la playlist
    r.delete(id)

    # Elimino la lista de canciones de la playlist
    r.delete(constantes.CLAVE_AUDIOS + ":" + id)
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE PLAYLISTS
#
#
#########################################################################################

# Funcion para obtener una playlist
def getLista(r, id):
    return r.hmget(id)

# Funcion para obtener el nombre de una playlist
def getNombreLista(r, id):
    return r.hget(id, constantes.CLAVE_NOMBRE_LISTA)

# Funcion para obtener el tipo de playlist (publica o privada)
def getPrivacidadLista(r, id):
    return r.hget(id, constantes.CLAVE_PRIVACIDAD_LISTA)

# Funcion para obtener el tipo de playlist (reproduccion o favoritos o ranking)
def getTipoLista(r, id):
    return r.hget(id, constantes.CLAVE_TIPO_LISTA)

# Funcion para obtener las canciones de una playlist
def getAudiosLista(r, id):
    stop = False
    iterador = 0
    canciones = []
    while not stop:
        scan = r.sscan(constantes.CLAVE_AUDIOS + ":" + id, iterador, count=100)
        canciones.extend(scan[1])
        iterador = scan[0]
        if iterador == 0:
            stop = True

    return canciones
    