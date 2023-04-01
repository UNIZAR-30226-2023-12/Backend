import redis
import Configuracion.constantesPrefijosClaves as constantesPrefijosClaves

listaClaves = [constantesPrefijosClaves.CLAVE_ID_NOTIFICACION, constantesPrefijosClaves.CLAVE_ID_USUARIO_EMISIOR, constantesPrefijosClaves.CLAVE_TIPO_NOTIFICACION, constantesPrefijosClaves.CLAVE_TITULO_NOTIFICACION, constantesPrefijosClaves.CLAVE_MENSAJE_NOTIFICACION]

def getIdContador(r):
    id = r.get(constantesPrefijosClaves.CLAVE_CONTADOR_NOTIFICACIONES)
    if(id == None):
        r.set(constantesPrefijosClaves.CLAVE_CONTADOR_NOTIFICACIONES, 0)
        id = 0
    pipe = r.pipeline()
    pipe.get(constantesPrefijosClaves.CLAVE_CONTADOR_NOTIFICACIONES)
    pipe.incr(constantesPrefijosClaves.CLAVE_CONTADOR_NOTIFICACIONES)
    id = pipe.execute()[0]
    return id


def guardarNotificacion(r, notificacionDiccionario):
    if (r.exists(notificacionDiccionario[constantesPrefijosClaves.CLAVE_ID_NOTIFICACION]) == 1 or notificacionDiccionario[constantesPrefijosClaves.CLAVE_ID_NOTIFICACION] == None
        or sorted(listaClaves) != sorted(list(notificacionDiccionario.keys()))):
        return -1
    else:
        id = notificacionDiccionario[constantesPrefijosClaves.CLAVE_ID_NOTIFICACION]
        del(notificacionDiccionario[constantesPrefijosClaves.CLAVE_ID_NOTIFICACION])
        r.hmset(id, notificacionDiccionario)
        return 0
    
def eliminarNotificacion(r, id):
    if(r.exists(id) == 0):
        return -1
    r.delete(id)
    return 0

