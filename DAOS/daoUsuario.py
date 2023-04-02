import redis
import Configuracion.constantesPrefijosClaves as constantes

#Numero de elementos que se devuelven en cada iteración de sscan
COUNT = 100

listaClaves = [constantes.CLAVE_ID_USUARIO, constantes.CLAVE_EMAIL, constantes.CLAVE_ALIAS, constantes.CLAVE_CONTRASENYA, constantes.CLAVE_TIPO_USUARIO]



def getIdContador(r):
    id = r.get(constantes.CLAVE_CONTADOR_USUARIOS)
    if(id == None):
        r.set(constantes.CLAVE_CONTADOR_USUARIOS, 1)
        id = 1
    pipe = r.pipeline()
    pipe.get(constantes.CLAVE_CONTADOR_USUARIOS)
    pipe.incr(constantes.CLAVE_CONTADOR_USUARIOS)
    id = pipe.execute()[0]
    return id

def setUsuario(r, usuarioDiccionario):
    id = usuarioDiccionario[constantes.CLAVE_ID_USUARIO]
    del(usuarioDiccionario[constantes.CLAVE_ID_USUARIO])
    return r.hmset(id, usuarioDiccionario)

def setEmail(r, id, email):
    return r.hset(id, constantes.CLAVE_EMAIL, email)

def setAlias(r, id, alias):
    return r.hset(id, constantes.CLAVE_ALIAS, alias)
    

def setContrasenya(r, id, contrasenya):
    return r.hset(id, constantes.CLAVE_CONTRASENYA, contrasenya)

def setTipoUsuario(r, id, tipoUsuario):
    return r.hset(id, constantes.CLAVE_TIPO_USUARIO, tipoUsuario)

def eliminarUsuario(r, id):
    return r.delete(id)

def tipoUsuarioValido(tipoUsuario):
    if(tipoUsuario == constantes.USUARIO_ADMINISTRADOR or tipoUsuario == constantes.USUARIO_NORMAL or tipoUsuario == constantes.constantesUsuario.USUARIO_ARTISTA):
        return True
    else:
        return False
    
def getUsuario(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hgetall(id)

def getEmail(r, id):
    return r.hget(id, constantes.CLAVE_EMAIL)

def getAlias(r, id):
    return r.hget(id, constantes.CLAVE_ALIAS)

def getContrasenya(r, id):
    return r.hget(id, constantes.CLAVE_CONTRASENYA)

def getTipoUsuario(r, id):
    return r.hget(id, constantes.CLAVE_TIPO_USUARIO)

def anyadirAmigo(r, id, idAmigo):
    return anyadirRelacion(r, id, idAmigo, constantes.CLAVE_AMIGOS)
    

def eliminarAmigo(r, id, idAmigo):
    return eliminarRelacion(r, id, idAmigo, constantes.CLAVE_AMIGOS)

def getAmigos(r, id):
    return getRelaciones(r, id, constantes.CLAVE_AMIGOS)

def anyadirArtista(r, id, idArtista):
    return anyadirRelacion(r, id, idArtista, constantes.CLAVE_ARTISTAS)

def eliminarArtista(r, id, idArtista):
    return eliminarRelacion(r, id, idArtista, constantes.CLAVE_ARTISTAS)

def getArtistas(r, id):
    return getRelaciones(r, id, constantes.CLAVE_ARTISTAS)  

def anyadirLista(r, id, idLista):
    return anyadirRelacion(r, id, idLista, constantes.CLAVE_LISTAS)

def eliminarLista(r, id, idLista):
    return eliminarRelacion(r, id, idLista, constantes.CLAVE_LISTAS)

def getListas(r, id):
    return getRelaciones(r, id, constantes.CLAVE_LISTAS)

def anyadirNotificacion(r, id, idNotificacion):
    return anyadirRelacion(r, id, idNotificacion, constantes.CLAVE_NOTIFICACIONES)

def eliminarNotificacion(r, id, idNotificacion):
    return eliminarRelacion(r, id, idNotificacion, constantes.CLAVE_NOTIFICACIONES)

def getNotificaciones(r, idNotificacion):
    return getRelaciones(r, id, constantes.CLAVE_NOTIFICACIONES)

def anyadirRelacion(r, idUsuario, idRealacion, prefijoRelacion):
    return r.sadd(prefijoRelacion + id, idRealacion)

def eliminarRelacion(r, idUsuario, idRealacion, prefijoRelacion):
    return r.srem(prefijoRelacion + id, idRealacion)

def getRelaciones(r, idUsuario, prefijoRelacion):
    parar = False
    cursor = 0
    relaciones = []

    while(parar == False):
        scan = r.sscan(prefijoRelacion + id, cursor, count=100)
        cursor = scan[0]
        relaciones.extend(scan[1])
        if(cursor == 0):
            parar = True
    return relaciones


# Funcion adicional de artista
def anyadirCancion(r, id, idCancion):
    return r.sadd(constantes.CLAVE_CANCIONES + id, idCancion)

def eliminarCancion(r, id, idCancion):
    return r.srem(constantes.CLAVE_CANCIONES + id, idCancion)

def getCanciones(r, id):
    parar = False
    cursor = 0
    canciones = []

    while(parar == False):
        scan = r.sscan(constantes.CLAVE_CANCIONES + id, cursor, count = COUNT)
        cursor = scan[0]
        canciones.extend(scan[1])
        if(cursor == 0):
            parar = True
    return canciones

# Función adicional de administrador
def anyadirAdministrador(r, id):
    return r.sadd(constantes.CLAVE_ADMINISTRADORES, id)

def eliminarAdministrador(r, id):
    return r.srem(constantes.CLAVE_ADMINISTRADORES, id)

def 