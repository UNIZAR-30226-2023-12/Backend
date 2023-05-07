import redis
import Configuracion.constantesPrefijosClaves as constantes

#Numero de elementos que se devuelven en cada iteración de sscan
COUNT = 100

# Lista de claves necesarias para crear un usuario
listaClaves = [constantes.CLAVE_EMAIL, constantes.CLAVE_ALIAS, 
               constantes.CLAVE_CONTRASENYA, constantes.CLAVE_TIPO_USUARIO]



def getIdContador(r):
    return constantes.PREFIJO_ID_USUARIO + ":" + str(r.incr(constantes.CLAVE_CONTADOR_USUARIOS))

def existeUsuario(r, idUsuario):
    if(r.exists(idUsuario) == 0):
        return False
    return True

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

def setImagenPerfil(r, idUsuario, imagenPerfil):
    return r.hset(idUsuario, constantes.CLAVE_IMAGEN_PERFIL, imagenPerfil)

def setUltimoAudio(r, idUsuario, idAudio):
    return r.hset(idUsuario, constantes.CLAVE_ID_ULTIMO_AUDIO, idAudio)

def eliminarUsuario(r, idUsuario):
    return r.delete(idUsuario)

def tipoUsuarioValido(tipoUsuario):
    if(tipoUsuario == constantes.USUARIO_ADMINISTRADOR or tipoUsuario == constantes.USUARIO_NORMAL or tipoUsuario == constantes.USUARIO_ARTISTA):
        return True
    else:
        return False
    
def getUsuario(r, idUsuario):
    return r.hgetall(idUsuario)

def getEmail(r, id):
    return r.hget(id, constantes.CLAVE_EMAIL)

def getAlias(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_ALIAS)

def getContrasenya(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_CONTRASENYA)

def setContrasenya(r, id, contrasenya):
    return r.hset(id, constantes.CLAVE_CONTRASENYA, contrasenya)

def getTipoUsuario(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_TIPO_USUARIO)

def getImagenPerfil(r, idUsuario):
    return r.hget(idUsuario, constantes.CLAVE_IMAGEN_PERFIL)

def anyadirAmigo(r, idUsuario, idAmigo):
    return anyadirRelacion(r, idUsuario, idAmigo, constantes.PREFIJO_AMIGOS)
    
def eliminarAmigo(r, idUsuario, idAmigo):
    return eliminarRelacion(r, idUsuario, idAmigo, constantes.PREFIJO_AMIGOS)

def getAmigos(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.PREFIJO_AMIGOS)

def anyadirArtista(r, idUsuario, idArtista):
    return anyadirRelacion(r, idUsuario, idArtista, constantes.PREFIJO_ARTISTAS_SUSCRITOS)

def eliminarArtista(r, idUsuario, idArtista):
    return eliminarRelacion(r, idUsuario, idArtista, constantes.PREFIJO_ARTISTAS_SUSCRITOS)

def getArtistas(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.PREFIJO_ARTISTAS_SUSCRITOS)  

def anyadirLista(r, idUsuario, idLista):
    return anyadirRelacion(r, idUsuario, idLista, constantes.CLAVE_LISTAS)

def eliminarLista(r, idUsuario, idLista):
    return eliminarRelacion(r, idUsuario, idLista, constantes.CLAVE_LISTAS)

def getListas(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.CLAVE_LISTAS)

def anyadirNotificacion(r, idUsuario, idNotificacion):
    return anyadirRelacion(r, idUsuario, idNotificacion, constantes.PREFIJO_NOTIFICACIONES)

def eliminarNotificacion(r, idUsuario, idNotificacion):
    return eliminarRelacion(r, idUsuario, idNotificacion, constantes.PREFIJO_NOTIFICACIONES)

def getNotificaciones(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.PREFIJO_NOTIFICACIONES)

def anyadirCarpeta(r, idUsuario, idCarpeta):
    return anyadirRelacion(r, idUsuario, idCarpeta, constantes.PREFIJO_CARPETAS)

def eliminarCarpeta(r, idUsuario, idCarpeta):
    return eliminarRelacion(r, idUsuario, idCarpeta, constantes.PREFIJO_CARPETAS)

def getCarpetas(r, idUsuario):
    return getRelaciones(r, idUsuario, constantes.PREFIJO_CARPETAS)

# Funciones para añadir, eliminar y obtener relaciones del usuario
def anyadirRelacion(r, idUsuario, idRealacion, prefijoRelacion):
    return r.sadd(prefijoRelacion + ":" + idUsuario, idRealacion)

def eliminarRelacion(r, idUsuario, idRealacion, prefijoRelacion):
    return r.srem(prefijoRelacion + ":" + idUsuario, idRealacion)

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
    return r.sadd(constantes.CLAVE_ADMINISTRADORES, id)

def eliminarAdministrador(r, id):
    return r.srem(constantes.CLAVE_ADMINISTRADORES, id)

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

# Funciones para crear set de ulimos Audios escuchados)
def setSegundosAudio(r, idUsuario, idAudio, segundos):
    return r.set(constantes.PREFIJO_SEGUNDOS_AUDIOS + ":" + idUsuario + ":" + idAudio, segundos)

def getSegundosAudio(r, idUsuario, idAudio):
    return r.get(constantes.PREFIJO_SEGUNDOS_AUDIOS + ":" + idUsuario + ":" + idAudio)

def eliminarSegundosAudio(r, idUsuario, idAudio):
    return r.delete(constantes.PREFIJO_SEGUNDOS_AUDIOS + ":" + idUsuario + ":" + idAudio)

# Daos para crear tabla hash email | idUsuario para agilizar el inicio de sesion
def setEmailId(r, email, idUsuario):
    return r.hset(constantes.CLAVE_HASH_EMAIL_ID, email, idUsuario)

def getIdEmailId(r, email):
    return r.hget(constantes.CLAVE_HASH_EMAIL_ID, email)

def eliminarEmailId(r, email):
    return r.hdel(constantes.CLAVE_HASH_EMAIL_ID, email)

def existeEmailId(r, email):
    if (r.hexists(constantes.CLAVE_HASH_EMAIL_ID, email) == 1):
        return True
    return False

def setCodigoRecuperacion(r, idUsuario, codigo):
    return r.set(constantes.PREFIJO_CODIGO_RECUPERACION + ":" + idUsuario, codigo)

def getCodigoRecuperacion(r, idUsuario):
    return r.get(constantes.PREFIJO_CODIGO_RECUPERACION + ":" + idUsuario)