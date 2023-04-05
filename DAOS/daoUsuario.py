import redis
import Configuracion.constantesPrefijosClaves as constantes

#Numero de elementos que se devuelven en cada iteración de sscan
COUNT = 100

listaClaves = [constantes.CLAVE_ID_USUARIO, constantes.CLAVE_EMAIL, 
               constantes.CLAVE_ALIAS, constantes.CLAVE_CONTRASENYA, 
               constantes.CLAVE_TIPO_USUARIO, constantes.CLAVE_ID_ULTIMO_AUDIO]



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
    idUsuario = usuarioDiccionario[constantes.CLAVE_ID_USUARIO]
    del(usuarioDiccionario[constantes.CLAVE_ID_USUARIO])
    return r.hmset(idUsuario, usuarioDiccionario)

def setEmail(r, idUsuario, email):
    return r.hset(idUsuario, constantes.CLAVE_EMAIL, email)

def setAlias(r, idUsuario, alias):
    return r.hset(idUsuario, constantes.CLAVE_ALIAS, alias)  

def setContrasenya(r, idUsuario, contrasenya):
    return r.hset(idUsuario, constantes.CLAVE_CONTRASENYA, contrasenya)

def setTipoUsuario(r, idUsuario, tipoUsuario):
    return r.hset(idUsuario, constantes.CLAVE_TIPO_USUARIO, tipoUsuario)

def setUltimaCancion(r, idUsuario, idAudio):
    return r.hset(idUsuario, constantes.CLAVE_ID_ULTIMO_AUDIO, idAudio)

def eliminarUsuario(r, idUsuario):
    return r.delete(idUsuario)

def tipoUsuarioValido(tipoUsuario):
    if(tipoUsuario == constantes.USUARIO_ADMINISTRADOR or tipoUsuario == constantes.USUARIO_NORMAL or tipoUsuario == constantes.constantesUsuario.USUARIO_ARTISTA):
        return True
    else:
        return False
    
def getUsuario(r, idUsuario):
    return r.hmget(idUsuario, listaClaves)

def getEmail(r, id):
    return r.hget(id, constantes.CLAVE_EMAIL)

def getAlias(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_ALIAS)

def getContrasenya(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_CONTRASENYA)

def getTipoUsuario(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_TIPO_USUARIO)

def getUltimaCancion(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_ID_ULTIMO_AUDIO)

def anyadirAmigo(r, idUsuario, idAmigo):
    return anyadirRelacion(r, idUsuario, idAmigo, constantes.CLAVE_AMIGOS)
    
def eliminarAmigo(r, idUsuario, idAmigo):
    return eliminarRelacion(r, idUsuario, idAmigo, constantes.CLAVE_AMIGOS)

def getAmigos(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.CLAVE_AMIGOS)

def anyadirArtista(r, idUsuario, idArtista):
    return anyadirRelacion(r, idUsuario, idArtista, constantes.CLAVE_ARTISTAS)

def eliminarArtista(r, idUsuario, idArtista):
    return eliminarRelacion(r, idUsuario, idArtista, constantes.CLAVE_ARTISTAS)

def getArtistas(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.CLAVE_ARTISTAS)  

def anyadirLista(r, idUsuario, idLista):
    return anyadirRelacion(r, idUsuario, idLista, constantes.CLAVE_LISTAS)

def eliminarLista(r, idUsuario, idLista):
    return eliminarRelacion(r, idUsuario, idLista, constantes.CLAVE_LISTAS)

def getListas(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.CLAVE_LISTAS)

def anyadirNotificacion(r, idUsuario, idNotificacion):
    return anyadirRelacion(r, idUsuario, idNotificacion, constantes.CLAVE_NOTIFICACIONES)

def eliminarNotificacion(r, idUsuario, idNotificacion):
    return eliminarRelacion(r, idUsuario, idNotificacion, constantes.CLAVE_NOTIFICACIONES)

def getNotificaciones(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.CLAVE_NOTIFICACIONES)

def anyadirCarpeta(r, idUsuario, idCarpeta):
    return anyadirRelacion(r, idUsuario, idCarpeta, constantes.CLAVE_CARPETAS)

def eliminarCarpeta(r, idUsuario, idCarpeta):
    return eliminarRelacion(r, idUsuario, idCarpeta, constantes.CLAVE_CARPETAS)

def getCarpetas(r, idUsuario, idCarpeta):
    return getRelaciones(r, idUsuario, idCarpeta, constantes.CLAVE_CARPETAS)

# Funciones para añadir, eliminar y obtener relaciones del usuario
def anyadirRelacion(r, idUsuario, idRealacion, prefijoRelacion):
    return r.sadd(prefijoRelacion + ":" + idUsuario, *idRealacion)

def eliminarRelacion(r, idUsuario, idRealacion, prefijoRelacion):
    return r.srem(prefijoRelacion + ":" + idUsuario, *idRealacion)

def getRelaciones(r, idUsuario, prefijoRelacion):
    parar = False
    cursor = 0
    relaciones = []

    while(parar == False):
        scan = r.sscan(prefijoRelacion + ":" + idUsuario, cursor, count=COUNT)
        cursor = scan[0]
        relaciones.extend(scan[1])
        if(cursor == 0):
            parar = True
    return relaciones


# Funcion adicional de artista
def anyadirCancion(r, idUsuario, idAudio):
    return anyadirRelacion(r, idUsuario, idAudio, constantes.CLAVE_CANCIONES)

def eliminarCancion(r, idUsuario, idAudio):
    return eliminarRelacion(r, idUsuario, idAudio, constantes.CLAVE_CANCIONES)

def getCanciones(r, id):
    return getRelaciones(r, id, constantes.CLAVE_CANCIONES)

# Función adicional de administrador
def anyadirAdministrador(r, id):
    return r.sadd(constantes.CLAVE_ADMINISTRADORES, *id)

def eliminarAdministrador(r, id):
    return r.srem(constantes.CLAVE_ADMINISTRADORES, *id)

def getAdministradores(r):
    parar = False
    cursor = 0
    administradores = []

    while(parar == False):
        scan = r.sscan(constantes.CLAVE_ADMINISTRADORES, cursor, count = COUNT)
        cursor = scan[0]
        administradores.extend(scan[1])
        if(cursor == 0):
            parar = True
    return administradores

def setUltimoSegundo(r, idUsuario, idAudio, segundo):
    return r.set(constantes.CLAVE_ULTIMO_SEGUNDO + ":" + idUsuario + ":" + idAudio, segundo)

def getUltimoSegundo(r, idUsuario, idAudio):
    return r.get(constantes.CLAVE_ULTIMO_SEGUNDO + ":" + idUsuario + ":" + idAudio)

def eliminarUltimoSegundo(r, idUsuario, idAudio):
    return r.delete(constantes.CLAVE_ULTIMO_SEGUNDO + ":" + idUsuario + ":" + idAudio)

# Daos para crear tabla hash email | idUsuario para agilizar el inicio de sesion
def setEmailId(r, email, idUsuario):
    return r.hset(constantes.CLAVE_HASH_EMAIL_ID, email, idUsuario)

def getIdEmailId(r, email):
    return r.hget(constantes.CLAVE_HASH_EMAIL_ID, email)

def eliminarEmailId(r, email):
    return r.hdel(constantes.CLAVE_HASH_EMAIL_ID, email)