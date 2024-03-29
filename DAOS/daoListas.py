import redis
import Configuracion.constantesPrefijosClaves as constantes


listaClaves = [constantes.CLAVE_NOMBRE_LISTA, 
               constantes.CLAVE_PRIVACIDAD_LISTA, 
               constantes.CLAVE_TIPO_LISTA,
               constantes.CLAVE_ID_USUARIO]

def getIdContador(r):
    return constantes.PREFIJO_ID_LISTA + ":" + str(r.incr(constantes.CLAVE_CONTADOR_LISTAS))

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

    r.sadd(constantes.CLAVE_LISTAS, id)

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

def setIDUsuario(r, idLista, idUsuario):
    return r.hset(idLista, constantes.CLAVE_ID_USUARIO, idUsuario)

# Funcion para añadir una o más canciones a una playlist
def anyadirAudioLista(r, idLista, idAudio):
    return r.sadd(constantes.CLAVE_AUDIOS + ":" + idLista, idAudio)

# Funcion para eliminar una o más canciones de una playlist
def eliminarAudioLista(r, idLista, idAudio):
    return r.srem(constantes.CLAVE_AUDIOS + ":" + idLista, idAudio)

# Funcion para eliminar una playlist
def eliminarLista(r, id):
    # Elimino la playlist
    r.delete(id)

#########################################################################################
#
#
# FUNCIONES PARA OBTENER DATOS DE PLAYLISTS
#
#
#########################################################################################

# Funcion para obtener una playlist
def getLista(r, id):
    return r.hgetall(id)

# Funcion para obtener el nombre de una playlist
def getNombreLista(r, id):
    return r.hget(id, constantes.CLAVE_NOMBRE_LISTA)

# Funcion para obtener el tipo de playlist (publica o privada)
def getPrivacidadLista(r, id):
    return r.hget(id, constantes.CLAVE_PRIVACIDAD_LISTA)

# Funcion para obtener el tipo de playlist (reproduccion o favoritos o ranking)
def getTipoLista(r, id):
    return r.hget(id, constantes.CLAVE_TIPO_LISTA)

def getIDUsuario(r, id):
    return r.hget(id, constantes.CLAVE_ID_USUARIO)

def obtenerTodasLasListas(r):
    return r.smembers(constantes.CLAVE_LISTAS)

def obtenerDatosListas(r, listas):
    datosListas = []

    for id in listas:
        datos = getLista(r, id)
        datos[constantes.CLAVE_ID_LISTA] = id
        datosListas.append(datos)

    return datosListas

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

def tipoListaValido(tipo):
    if tipo == constantes.LISTA_TIPO_REPRODUCCION or tipo == constantes.LISTA_TIPO_FAVORITOS or tipo == constantes.LISTA_TIPO_RANKING:
        return True
    return False
    