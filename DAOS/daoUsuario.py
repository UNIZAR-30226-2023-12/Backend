import redis
import Configuracion.constantesPrefijosClaves as constantesPrefijosClaves

#Numero de elementos que se devuelven en cada iteración de sscan
COUNT = 100

listaClaves = [constantesPrefijosClaves.CLAVE_ID_USUARIO, constantesPrefijosClaves.CLAVE_EMAIL, constantesPrefijosClaves.CLAVE_ALIAS, constantesPrefijosClaves.CLAVE_CONTRASENYA, constantesPrefijosClaves.CLAVE_TIPO_USUARIO]





def guardarUsuario(r, usuarioDiccionario):
    if (sorted(listaClaves) != sorted(list(usuarioDiccionario.keys())) or usuarioDiccionario[constantesPrefijosClaves.CLAVE_ID_USUARIO] == None
        or r.exists(usuarioDiccionario[constantesPrefijosClaves.CLAVE_ID_USUARIO]) == 1 or (tipoUsuarioValido(usuarioDiccionario[constantesPrefijosClaves.CLAVE_TIPO_USUARIO]) == False)):
        return -1
    else:
        id = usuarioDiccionario[constantesPrefijosClaves.CLAVE_ID_USUARIO]
        del(usuarioDiccionario[constantesPrefijosClaves.CLAVE_ID_USUARIO])
        r.hmset(id, usuarioDiccionario)
        return 0

def cambiarEmail(r, id, email):
    if (r.exists(id) == 0 or email == None):
        return -1
    r.hset(id, constantesPrefijosClaves.CLAVE_EMAIL, email)
    return 0

def cambiarAlias(r, id, alias):
    if(r.exists(id) == 0 or alias == None):
        return -1
    r.hset(id, constantesPrefijosClaves.CLAVE_ALIAS, alias)
    return 0

def cambiarContrasenya(r, id, contrasenya):
    if(r.exists(id) == 0 or contrasenya == None):
        return -1
    r.hset(id, constantesPrefijosClaves.CLAVE_CONTRASENYA, contrasenya)

def cambiarTipoUsuario(r, id, tipoUsuario):
    if(r.exists(id) == 0 or tipoUsuario == None or not tipoUsuarioValido(tipoUsuario)):
        return -1
    r.hset(id, constantesPrefijosClaves.CLAVE_TIPO_USUARIO, tipoUsuario)
    return 0

def eliminarUsuario(r, id):
    if(r.exists(id) == 0):
        return -1
    r.delete(id)
    return 0

def tipoUsuarioValido(tipoUsuario):
    if(tipoUsuario == constantesPrefijosClaves.USUARIO_ADMINISTRADOR or tipoUsuario == constantesPrefijosClaves.USUARIO_NORMAL or tipoUsuario == constantesPrefijosClaves.constantesUsuario.USUARIO_ARTISTA):
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
    return r.hget(id, constantesPrefijosClaves.CLAVE_EMAIL)

def obtenerAlias(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, constantesPrefijosClaves.CLAVE_ALIAS)

def obtenerContrasenya(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, constantesPrefijosClaves.CLAVE_CONTRASENYA)

def obtenerTipoUsuario(r, id):
    if(r.exists(id) == 0):
        return -1
    return r.hget(id, constantesPrefijosClaves.CLAVE_TIPO_USUARIO)

def anyadirAmigo(r, id, idAmigo):
    if(r.exists(id) == 0 or r.exists(idAmigo) == 0):
        return -1
    r.sadd(constantesPrefijosClaves.CLAVE_AMIGOS + id, idAmigo)
    return 0

def eliminarAmigo(r, id, idAmigo):
    if(r.exists(id) == 0 or r.exists(idAmigo) == 0):
        return -1
    r.srem(constantesPrefijosClaves.CLAVE_AMIGOS + id, idAmigo)
    return 0

def obtenerAmigos(r, id):
    parar = False
    cursor = 0
    amigos = []
    if(r.exists(id) == 0):
        return -1
    
    while(parar == False):
        scan = r.sscan(constantesPrefijosClaves.CLAVE_AMIGOS + id, cursor, count = COUNT)
        cursor = scan[0]
        amigos.extend(scan[1])
        if(cursor == 0):
            parar = True
    return amigos

def suscribirArtista(r, id, idArtista):
    if(r.exists(id) == 0 or r.exists(idArtista) == 0 or 
       r.hget(idArtista, constantesPrefijosClaves.CLAVE_TIPO_USUARIO) != constantesPrefijosClaves.USUARIO_ARTISTA):
        return -1
    r.sadd(constantesPrefijosClaves.CLAVE_ARTISTAS + id, idArtista)
    return 0

def desuscribirArtista(r, id, idArtista):
    if(r.exists(id) == 0 or r.exists(idArtista) == 0 or 
       r.hget(idArtista, constantesPrefijosClaves.CLAVE_TIPO_USUARIO) != constantesPrefijosClaves.USUARIO_ARTISTA):
        return -1
    r.srem(constantesPrefijosClaves.CLAVE_ARTISTAS + str(id), idArtista)
    return 0

def obtenerArtistasSuscritos(r, id):
    if(r.exists(id) == 0):
        return -1
    parar = False
    cursor = 0
    artistas = []

    while(parar == False):
        scan = r.sscan(constantesPrefijosClaves.CLAVE_ARTISTAS + id, cursor, count = COUNT)
        cursor = scan[0]
        artistas.extend(scan[1])
        if(cursor == 0):
            parar = True
    return artistas  