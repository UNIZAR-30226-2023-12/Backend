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


def guardarNotificacion(r, notificacionDiccionario):
    if (r.exists(notificacionDiccionario[constantes.CLAVE_ID_NOTIFICACION]) == 1 or notificacionDiccionario[constantes.CLAVE_ID_NOTIFICACION] == None
        or sorted(listaClaves) != sorted(list(notificacionDiccionario.keys()))):
        return -1
    else:
        id = notificacionDiccionario[constantes.CLAVE_ID_NOTIFICACION]
        del(notificacionDiccionario[constantes.CLAVE_ID_NOTIFICACION])
        r.hmset(id, notificacionDiccionario)
        return 0
    
def eliminarNotificacion(r, id):
    if(r.exists(id) == 0):
        return -1
    r.delete(id)
    return 0

