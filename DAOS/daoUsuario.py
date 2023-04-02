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
    return r.sadd(constantes.CLAVE_AMIGOS + id, idAmigo)
    

def eliminarAmigo(r, id, idAmigo):
    return r.srem(constantes.CLAVE_AMIGOS + id, idAmigo)

def getAmigos(r, id):
    parar = False
    cursor = 0
    amigos = []

    while(parar == False):
        scan = r.sscan(constantes.CLAVE_AMIGOS + id, cursor, count = COUNT)
        cursor = scan[0]
        amigos.extend(scan[1])
        if(cursor == 0):
            parar = True
    return amigos

def anyadirArtista(r, id, idArtista):
    return r.sadd(constantes.CLAVE_ARTISTAS + id, idArtista)

def eliminarArtista(r, id, idArtista):
    return r.srem(constantes.CLAVE_ARTISTAS + str(id), idArtista)

def getArtistas(r, id):
    parar = False
    cursor = 0
    artistas = []

    while(parar == False):
        scan = r.sscan(constantes.CLAVE_ARTISTAS + id, cursor, count = COUNT)
        cursor = scan[0]
        artistas.extend(scan[1])
        if(cursor == 0):
            parar = True
    return artistas  

def anyadirLista(r, id, idLista):
    return r.sadd(constantes.CLAVE_LISTAS + id, idLista)

def eliminarLista(r, id, idLista):
    return r.srem(constantes.CLAVE_LISTAS + id, idLista)

def getListas(r, id):
    parar = False
    cursor = 0
    listas = []

    while(parar == False):
        scan = r.sscan(constantes.CLAVE_LISTAS + id, cursor, count=100)
        cursor = scan[0]
        listas.extend(scan[1])
        if(cursor == 0):
            parar = True
    return listas  

# Funcion adicional de artista
def anyadirCancion(r, id, idCancion):
    return r.sadd(constantes.CLAVE_CANCIONES + id, idCancion)

def eliminarCancion(r, id, idCancion):
    return r.srem(constantes.CLAVE_CANCIONES + id, idCancion)

def obtenerCanciones(r, id):
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