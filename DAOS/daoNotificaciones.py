import redis
import Configuracion.constantesPrefijosClaves as constantes

listaClaves = [constantes.CLAVE_ID_NOTIFICACION, constantes.CLAVE_ID_USUARIO_EMISIOR, constantes.CLAVE_TIPO_NOTIFICACION, constantes.CLAVE_TITULO_NOTIFICACION, constantes.CLAVE_MENSAJE_NOTIFICACION]

def getIdContador(r):
    id = r.get(constantes.CLAVE_CONTADOR_NOTIFICACIONES)
    if(id == None):
        r.set(constantes.CLAVE_CONTADOR_NOTIFICACIONES, 0)
        id = 0
    pipe = r.pipeline()
    pipe.get(constantes.CLAVE_CONTADOR_NOTIFICACIONES)
    pipe.incr(constantes.CLAVE_CONTADOR_NOTIFICACIONES)
    id = pipe.execute()[0]
    return id


def setNotificacion(r, notificacionDiccionario):
    id = notificacionDiccionario[constantes.CLAVE_ID_NOTIFICACION]
    del(notificacionDiccionario[constantes.CLAVE_ID_NOTIFICACION])
    r.hmset(id, notificacionDiccionario)

def setIdUsuarioEmisor(r, id, idUsuarioEmisor):
    return r.hset(id, constantes.CLAVE_ID_USUARIO_EMISIOR, idUsuarioEmisor)

def setTipoNotificacion(r, id, tipoNotificacion):
    return r.hset(id, constantes.CLAVE_TIPO_NOTIFICACION, tipoNotificacion)

def setTituloNotificacion(r, id, tituloNotificacion):
    return r.hset(id, constantes.CLAVE_TITULO_NOTIFICACION, tituloNotificacion)

def setMensajeNotificacion(r, id, mensajeNotificacion):
    return r.hset(id, constantes.CLAVE_MENSAJE_NOTIFICACION, mensajeNotificacion)
    
def eliminarNotificacion(r, id):
    return r.delete(id)

def getNotificacion(r, id):
    return r.hgetall(id)

def getIdUsuarioEmisor(r, id):
    return r.hget(id, constantes.CLAVE_ID_USUARIO_EMISIOR)

def getTipoNotificacion(r, id):
    return r.hget(id, constantes.CLAVE_TIPO_NOTIFICACION)

def getTituloNotificacion(r, id):
    return r.hget(id, constantes.CLAVE_TITULO_NOTIFICACION)

def getMensajeNotificacion(r, id):
    return r.hget(id, constantes.CLAVE_MENSAJE_NOTIFICACION)

