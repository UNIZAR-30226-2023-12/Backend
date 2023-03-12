import redis
#Constantes simbólicas de las claves de los atributos de usuario
CLAVE_ID = "id"
CLAVE_EMAIL = "email"
CLAVE_ALIAS = "alias"
CLAVE_CONTRASENYA = "contrasenya"
CLAVE_TIPO_USUARIO = "tipoUsuario"
CLAVE_AMIGOS = "amigos"
CLAVE_ARTISTAS = "artista"
CLAVE_LISTAS = "listas"
#Constantes simbólicas de los tipos de usuario
USUARIO_ADMINISTRADOR = "admin"
USUARIO_NORMAL = "normalUser"
USUARIO_ARTISTA = "artista"
#Otras constantes simbólicas
COUNT = 100

listaClaves = [CLAVE_ID, CLAVE_EMAIL, CLAVE_ALIAS, CLAVE_CONTRASENYA, CLAVE_TIPO_USUARIO]





def guardarUsuario(r, usuarioDiccionario):
    if (sorted(listaClaves) != sorted(list(usuarioDiccionario.keys())) or usuarioDiccionario[CLAVE_ID] == None
        or r.exists(usuarioDiccionario[CLAVE_ID]) == 1 or (tipoUsuarioValido(usuarioDiccionario[CLAVE_TIPO_USUARIO]) == False)):
        return -1
    else:
        id = usuarioDiccionario[CLAVE_ID]
        del(usuarioDiccionario[CLAVE_ID])
        r.hmset(id, usuarioDiccionario)
        return 0

def cambiarEmail(r, id, email):
    if (r.exists(id) == 0 or email == None):
        return -1
    r.hset(id, CLAVE_EMAIL, email)
    return 0

def cambiarAlias(r, id, alias):
    if(r.exists(id) == 0 or alias == None):
        return -1
    r.hset(id, CLAVE_ALIAS, alias)
    return 0

def cambiarContrasenya(r, id, contrasenya):
    if(r.exists(id) == 0 or contrasenya == None):
        return -1
    r.hset(id, CLAVE_CONTRASENYA, contrasenya)

def cambiarTipoUsuario(r, id, tipoUsuario):
    if(r.exists(id) == 0 or tipoUsuario == None):
        return -1
    r.hset(id, CLAVE_TIPO_USUARIO, tipoUsuario)
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

def obtenerEmail(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, CLAVE_EMAIL)

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
    parar = False
    cursor = 0
    amigos = []
    if(r.exists(id) == 0):
        return -1
    
    while(parar == False):
        scan = r.sscan(CLAVE_AMIGOS + id, cursor, count = COUNT)
        cursor = scan[0]
        amigos.extend(scan[1])
        if(cursor == 0):
            parar = True
    return amigos

def suscribirArtista(r, id, idArtista):
    if(r.exists(id) == 0 or r.exists(idArtista) == 0 or 
       r.hget(idArtista, CLAVE_TIPO_USUARIO) != USUARIO_ARTISTA):
        return -1
    r.sadd(CLAVE_ARTISTAS + id, idArtista)
    return 0

def desuscribirArtista(r, id, idArtista):
    if(r.exists(id) == 0 or r.exists(idArtista) == 0 or 
       r.hget(idArtista, CLAVE_TIPO_USUARIO) != USUARIO_ARTISTA):
        return -1
    r.srem(CLAVE_ARTISTAS + str(id), idArtista)
    return 0

def obtenerArtistasSuscritos(r, id):
    if(r.exists(id) == 0):
        return -1
    parar = False
    cursor = 0
    artistas = []

    while(parar == False):
        scan = r.sscan(CLAVE_ARTISTAS + id, cursor, count = COUNT)
        cursor = scan[0]
        artistas.extend(scan[1])
        if(cursor == 0):
            parar = True
    return artistas  

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
    parar = False
    cursor = 0
    listas = []

    while(parar == False):
        scan = r.sscan(CLAVE_LISTAS + id, cursor, count=COUNT)
        cursor = scan[0]
        listas.extend(scan[1])
        if(cursor == 0):
            parar = True
    return listas  