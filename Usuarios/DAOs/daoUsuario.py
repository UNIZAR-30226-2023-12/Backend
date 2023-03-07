#Constantes simbólicas de las claves de los atributos de usuario
CLAVE_ID = "email"
CLAVE_ALIAS = "alias"
CLAVE_CONTRASENYA = "contrasenya"
CLAVE_TIPO_USUARIO = "tipoUsuario"
CLAVE_AMIGOS = "amigos"
CLAVE_ARTISTA = "artista"
CLAVE_LISTAS = "listas"
#Constantes simbólicas de los tipos de usuario
USUARIO_ADMINISTRADOR = "admin"
USUARIO_NORMAL = "normalUser"
USUARIO_ARTISTA = "artista"

listaClaves = [CLAVE_ID, CLAVE_ALIAS, CLAVE_CONTRASENYA, CLAVE_TIPO_USUARIO]

import redis




def guardarUsuario(r, usuarioDiccionario):
    if (listaClaves != list(usuarioDiccionario.keys()) or usuarioDiccionario["email"] == None
        or r.exists(usuarioDiccionario["email"]) == 1 or tipoUsuarioValido(usuarioDiccionario["tipoUsuario"]) == False):
        return -1
    else:
        id = usuarioDiccionario["email"]
        del(usuarioDiccionario["email"])
        r.hmset(id, usuarioDiccionario)
        return 0

def cambiarEmail(r, emailAnterior, emailNuevo):
    if (r.exists(emailNuevo) == 1 or r.exists(emailAnterior) == 0
        or emailAnterior == None or emailNuevo == None or emailAnterior == emailNuevo):
        return -1
    valores = r.hgetall(emailAnterior)
    r.delete(emailAnterior)
    r.hmset(emailNuevo, valores)
    return 0

def cambiarAlias(r, id, alias):
    if(r.exists(id) == 0 or alias == None):
        return -1
    r.hset(id, CLAVE_ALIAS, alias)
    return 0

def cambiarContrasenya(r, id, contrasenya):
    if(r.exists(id) == 0 or contrasenya == None):
        return -1
    r.hset(id, contrasenya)

def cambiarTipoUsuario(r, id, tipoUsuario):
    if(r.exists(id) == 0 or tipoUsuario == None):
        return -1
    r.hset(id, tipoUsuario)
    return 0

def eliminarUsuario(r, id):
    if(r.exists(id) == 0):
        return -1
    r.delete(id)
    return 0

def tipoUsuarioValido(tipoUsuario):
    if(tipoUsuario == USUARIO_ADMINISTRADOR or tipoUsuario == USUARIO_NORMAL or tipoUsuario == USUARIO_ARTISTA):
        return True
    else:
        return False
    
def obtenerUsuario(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hgetall(id)

def obtenerAlias(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, CLAVE_ALIAS)

def obtenerContrasenya(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, CLAVE_CONTRASENYA)

def obtenerTipoUsuario(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, CLAVE_TIPO_USUARIO)

def anyadirAmigo(r, id, idAmigo):
    if(r.exists(id) == 0 or r.exists(idAmigo) == 0):
        return -1
    r.sadd(CLAVE_AMIGOS + id, idAmigo)
    return 0

def eliminarAmigo(r, id, idAmigo):
    if(r.exists(id) == 0 or r.exists(idAmigo) == 0):
        return -1
    r.srem(CLAVE_AMIGOS + id, idAmigo)
    return 0

def obtenerAmigos(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.smembers(CLAVE_AMIGOS + id)

def suscribirArtista(r, id, idArtista):
    if(r.exists(id) == 0 or r.exists(idArtista) == 0 or 
       r.hget(idArtista, CLAVE_TIPO_USUARIO) != USUARIO_ARTISTA):
        return -1
    r.sadd(CLAVE_ARTISTA + id, idArtista)
    return 0

def desuscribirArtista(r, id, idArtista):
    if(r.exists(id) == 0 or r.exists(idArtista) == 0 or 
       r.hget(idArtista, CLAVE_TIPO_USUARIO) != USUARIO_ARTISTA):
        return -1
    r.srem(CLAVE_ARTISTA + id, idArtista)
    return 0

def obtenerArtistasSuscritos(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.smembers(CLAVE_ARTISTA + id)

def anyadirLista(r, id, idLista):
    if(r.exists(id) == 0 or r.exists(idLista) == 0):
        return -1
    r.sadd(CLAVE_LISTAS + id, idLista)
    return 0

def eliminarLista(r, id, idLista):
    if(r.exists(id) == 0 or r.exists(idLista) == 0):
        return -1
    r.srem(CLAVE_LISTAS + id, idLista)
    return 0

def obtenerListas(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.smembers(CLAVE_LISTAS + id)   