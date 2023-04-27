# Módulo usuarios, con funciones de alto nivel para la api
import redis
import DAOS.daoListas as daoListas
import DAOS.daoUsuario as daoUsuario
import DAOS.daoNotificaciones as daoNotificaciones
import DAOS.daoCarpetas as daoCarpetas
import DAOS.daoAudio as daoAudios
import Configuracion.constantesPrefijosClaves as constantes
import Configuracion.constantesErroresHTTP as erroresHTTP

# Funciones de usuarios normales

def existeUsuario(r, id):
    return daoUsuario.existeUsuario(r, id)

def existeNotificacion(r, id):
    return daoNotificaciones.existeNotificacion(r, id)

def existeLista(r, id):
    return daoListas.existeLista(r, id)

def existeCarpeta(r, id):
    return daoCarpetas.existeCarpeta(r, id)


def setUser(r, usuarioDiccionario):
    id = daoUsuario.getIdContador(r)
    usuarioDiccionario[constantes.CLAVE_ID_USUARIO] = id

    if(sorted(usuarioDiccionario.keys()) != sorted(daoUsuario.listaClaves)):
        respuesta = {"status": erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS}
        return respuesta
    
    if(daoUsuario.existeEmailId(r, usuarioDiccionario[constantes.CLAVE_EMAIL])):
        respuesta = {"status": erroresHTTP.ERROR_USUARIO_EMAIL_YA_EXISTE}
        return respuesta

    # Si el usuario es administrador lo añadimos a la lista de administradores
    if(usuarioDiccionario[constantes.CLAVE_TIPO_USUARIO] == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.anyadirAdministrador(r, id)
        
    # Guardamos el usuario en la base de datos    
    daoUsuario.setUsuario(r, usuarioDiccionario)

    # Lo añadimos al hash con la clave como email y el valor como id
    daoUsuario.setEmailId(r, usuarioDiccionario[constantes.CLAVE_EMAIL], id)
    respuesta = {"status": erroresHTTP.OK, constantes.CLAVE_ID_USUARIO: id}
    return respuesta


def getUser(r, id):
    if(daoUsuario.existeUsuario(r, id) == False):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    return daoUsuario.getUsuario(r, id)


def removeUser(r, id, contrasenya):
    if(r.exists(id) == 0):
        return -1
    amigos = daoUsuario.getAmigos(r, id)
    #Eliminar usuario de la lista de amigos de sus amigos
    for amigo in amigos:
        daoUsuario.eliminarAmigo(r, amigo, id)

    #Eliminar los sets de amigos, artistas, listas del usuario, notificaciones y carpetas
    r.delete(constantes.PREFIJO_AMIGOS + id)
    r.delete(constantes.PREFIJO_ARTISTAS_SUSCRITOS + id)
    r.delete(constantes.CLAVE_LISTAS + id)
    r.delete(constantes.PREFIJO_NOTIFICACIONES + id)
    r.delete(constantes.PREFIJO_CARPETAS + id)

    #Si es administrador, eliminarlo de la lista de administradores
    if(daoUsuario.getTipoUsuario(r, id) == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.eliminarAdministrador(r, id)
    daoUsuario.eliminarUsuario(r, id)
    return 1

def AskAdminToBeArtist(r, idUsuario):
    if(existeUsuario(r, idUsuario) == False):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
        
    idNotificacion = daoNotificaciones.getIdContador(r)
    diccionarioNotificaciones = {constantes.CLAVE_ID_NOTIFICACION: idNotificacion, 
                                 constantes.CLAVE_ID_USUARIO_EMISIOR: idUsuario, 
                                 constantes.CLAVE_TIPO_NOTIFICACION: constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA,
                                 constantes.CLAVE_TITULO_NOTIFICACION: constantes.TITULO_NOTIFICACION_ARTISTA,
                                 constantes.CLAVE_MENSAJE_NOTIFICACION: daoUsuario.getAlias(r,) + constantes.MENSAJE_NOTIFICACION_ARTISTA}
    daoNotificaciones.setNotificacion(r, diccionarioNotificaciones)
    administradores = daoUsuario.getAdministradores(r)
    for admin in administradores:
        daoUsuario.anyadirNotificacion(r, admin, idNotificacion)
    return erroresHTTP.OK
    
def ValidateUser(r, id, contrasenya):
    if (existeUsuario(r, id) == False): 
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    
    if (daoUsuario.getContrasenya(r, id) == contrasenya):
        return erroresHTTP.OK

    return erroresHTTP.ERROR_CONTRASENYA_INCORRECTA

def validateUserEmail(r, email, contrasenya):
    if (daoUsuario.existeEmailId(r, email) == False):
        respuesta = {"status": erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}
        return respuesta
    idUsuario = daoUsuario.getIdEmailId(r, email)
    status = ValidateUser(r, idUsuario, contrasenya)
    respuesta = {"status": status, constantes.CLAVE_ID_USUARIO : idUsuario}
    return respuesta

def setLastSecondHeard(r, idUsuario, idAudio, segundo):
    if (r.exists(idUsuario) == 0 or r.exists(idAudio) == 0):
        return -2
    daoUsuario.setUltimoSegundo(r, idUsuario, idAudio, segundo)
    return 1

def getLastSecondHeard(r, idUsuario, idAudio):
    if (r.exists(idUsuario) == 0 or r.exists(idAudio) == 0):
        return -2
    segundo = daoUsuario.getUltimoSegundo(r, idUsuario, idAudio)

    # En caso de que no exista devolvemos que va por el segundo 0
    if (segundo == None):
        return 0
    return segundo

# Funciones adicionales de artistas


# Funciones adcionales de administradores
def acceptArtist(r, idNotificacion):
    idUsuario = daoNotificaciones.getIdUsuarioEmisor(r, idNotificacion)
    if(existeUsuario(idUsuario)):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    if(daoNotificaciones.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA):
        return erroresHTTP.ERROR_NOTIFICACION_NO_SOLICITUD_ARTISTA
    
    # Eliminamos la notificación a los administradores
    administradores = daoUsuario.getAdministradores(r)
    for admin in administradores:
        daoUsuario.eliminarNotificacion(r, admin, idNotificacion)
    
    daoUsuario.setTipoUsuario(r, idUsuario, daoUsuario.constantes.USUARIO_ARTISTA)
    return erroresHTTP.OK

def esAdministrador(r, id):
    if (r.exists(id) == 0):
        return False
    return daoUsuario.getTipoUsuario(r, id) == constantes.USUARIO_ADMINISTRADOR


# Funciones de listas de reproducción
def setLista(r, idUsuario, diccionarioLista):
    id = daoListas.getIdContador(r)
    diccionarioLista[constantes.CLAVE_ID_LISTA] = id

    if(sorted(diccionarioLista) != sorted(daoListas.listaClaves)):
        return erroresHTTP.ERROR_LISTA_PARAMETROS_INCORRECTOS
    
    daoListas.setLista(r, diccionarioLista) 
    daoUsuario.anyadirLista(r, idUsuario, id)
    return erroresHTTP.OK

def setNombreLista(r, idLista, nombre):
    if (existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    
    return daoListas.setNombreLista(r, idLista, nombre)

def setSongLista(r, idLista, idAudio):
    if(existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    daoListas.anyadirAudioLista(r, idLista, idAudio)

    return erroresHTTP.OK

def setPrivacyLista(r, idUsuario, idLista, publica):
    if (r.exists(idUsuario) == 0):
        return -2
    if (r.exists(idLista) == 0):
        return -1
    daoListas.setPrivacidadLista(r, idLista, publica)
    return 1

def removeLista(r, idUsuario, idLista):
    if (r.exists(idUsuario) == 0):
        return -2
    if (r.exists(idLista) == 0):
        return -1
    daoListas.eliminarLista(r, idLista)
    daoUsuario.eliminarLista(r, idUsuario, idLista)
    return 1

def getLista(r, idLista):
    if(existeLista(r, idLista) == False):
        respuesta = {"status": erroresHTTP.ERROR_LISTA_NO_ENCONTRADA}
        return respuesta
    
    respuesta = {"status": erroresHTTP.OK, constantes.PREFIJO_ID_LISTA : daoListas.getLista(r, idLista)}
    return respuesta

def getListasUsr(r, idUsuario):
    return daoUsuario.getListas(r, idUsuario)

def getAudiosLista(r, idLista):
    return daoListas.getAudiosLista(r, idLista)

def getSongsArtist(r, idArtista):
    if(r.exists(idArtista) == 0):
        return -1
    return daoUsuario.getCanciones(r, idArtista)



def removeSongLista(r, idLista, idAudio):
    if (daoListas.existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    
    if (daoAudios.existeCancion(r, idAudio) == False):
        return erroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    daoListas.eliminarAudioLista(r, idLista, idAudio)
    return erroresHTTP.OK

# Funciones para carpetas
def setFolder(r, idUsuario, diccionarioCarpeta):
    id = daoCarpetas.getIdContador(r)
    diccionarioCarpeta[constantes.CLAVE_ID_CARPETA] = id

    if(sorted(diccionarioCarpeta) != sorted(daoCarpetas.carpetasClaves)):
        return erroresHTTP.ERROR_CARPETA_PARAMETROS_INCORRECTOS
    
    daoCarpetas.setCarpeta(r, diccionarioCarpeta) 
    daoUsuario.anyadirCarpeta(r, idUsuario, id)
    return erroresHTTP.OK

def addListToFolder(r, idCarpeta, idLista):
    if (existeCarpeta(r, idCarpeta) == False):
        return erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA
    if (existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    daoCarpetas.anyadirListaCarpeta(r, idCarpeta, idLista)
    return erroresHTTP.OK

def removeListFromFolder(r, idCarpeta, idLista):
    if (existeCarpeta(r, idCarpeta) == False):
        return erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA
    if (existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    if(daoCarpetas.eliminarListaCarpeta(r, idCarpeta, idLista) == 0):
        return erroresHTTP.ERROR_CARPETA_NO_TIENE_LISTA
    return erroresHTTP.OK
    
def removeFolder(r, idUsuario, idCarpeta):
    if (existeCarpeta(r, idCarpeta) == False):
        return erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA
    daoCarpetas.eliminarCarpeta(r, idCarpeta)
    daoUsuario.eliminarCarpeta(r, idUsuario, idCarpeta)
    return erroresHTTP.OK

def getFolder(r, idCarpeta):
    if(existeCarpeta(r, idCarpeta) == False):
        respuesta = {"status": erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA}
        return respuesta
    respuesta = {"status": erroresHTTP.OK, constantes.PREFIJO_ID_CARPETA : daoCarpetas.getCarpeta(r, idCarpeta)}
    return respuesta

def getListasFolder(r, idCarpeta):
    if(existeCarpeta(r, idCarpeta) == False):
        respuesta = {"status": erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA}
        return respuesta
    respuesta = {"status": erroresHTTP.OK, constantes.PREFIJO_ID_LISTA : daoCarpetas.getListasCarpeta(r, idCarpeta)}
    return respuesta

def getFoldersUser(r, idUsuario):
    if(existeUsuario(r, idUsuario) == False):
        respuesta = {"status": erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}
        return respuesta
    respuesta = {"status": erroresHTTP.OK, constantes.PREFIJO_ID_CARPETA : daoUsuario.getCarpetas(r, idUsuario)}
    return respuesta

def getPublicFoldersUser(r, idUsuario):
    folders = getFoldersUser(r, idUsuario)
    if(folders["status"] != erroresHTTP.OK):
        return folders
    folders = folders[constantes.PREFIJO_ID_CARPETA]
    publicFolders = []
    for folder in folders:
        if(daoCarpetas.esPublica(r, folder)):
            publicFolders.append(folder)
    respuesta = {"status": erroresHTTP.OK, constantes.PREFIJO_ID_CARPETA : publicFolders}
    return respuesta

# Funciones para gestionar amigos
def askFriend(r, idUsuario, idUsuarioAmigo):
    if(existeUsuario(r, idUsuario) == False):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    if(existeUsuario(r, idUsuarioAmigo) == False):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    if(idUsuario in daoUsuario.getAmigos(r, idUsuarioAmigo)):
        return erroresHTTP.ERROR_USUARIO_YA_AMIGO
    
    idNotificacion = daoNotificaciones.getIdContador(r)
    diccionarioNotificacion = {constantes.CLAVE_ID_NOTIFICACION: idNotificacion,
                               constantes.CLAVE_ID_USUARIO_EMISIOR: idUsuario,
                               constantes.CLAVE_TIPO_NOTIFICACION: constantes.NOTIFICACION_TIPO_AMIGO,
                               constantes.CLAVE_TITULO_NOTIFICACION: "Solicitud de amistad",
                               constantes.CLAVE_MENSAJE_NOTIFICACION: "El usuario " + daoUsuario.getAlias(r, idUsuario) + " quiere ser tu amigo"} 
    daoNotificaciones.setNotificacion(r, diccionarioNotificacion)
    daoUsuario.anyadirNotificacion(r, idUsuarioAmigo, idNotificacion)
    return erroresHTTP.OK

def accpetFriend(r, idUsuario, idNotificacion):
    if(existeNotificacion(r, idNotificacion) == False):
        return erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA
    if(daoNotificaciones.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_AMIGO):
        return erroresHTTP.ERROR_NOTIFICACION_NO_AMIGO
    idUsuarioAmigo = daoNotificaciones.getIdUsuarioEmisor(r, idNotificacion)    
    daoUsuario.anyadirAmigo(r, idUsuarioAmigo, idUsuario)
    daoUsuario.anyadirAmigo(r, idUsuario, idUsuarioAmigo)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)
    daoUsuario.eliminarNotificacion(r, idUsuario, idNotificacion)
    return erroresHTTP.OK

def getFriends(r, idUsuario):
    if(existeUsuario(r, idUsuario) == False):
        respuesta = {"status": erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}
        return respuesta
    respuesta = {"status": erroresHTTP.OK, constantes.PREFIJO_ID_USUARIO : daoUsuario.getAmigos(r, idUsuario)}
    return respuesta


def removeFriend(r, idUsuario, idUsuarioAmigo):
    if(existeUsuario(r, idUsuario) == False):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    if(existeUsuario(r, idUsuarioAmigo) == False):
        return erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO
    if(idUsuarioAmigo not in daoUsuario.getAmigos(r, idUsuario)):
        return erroresHTTP.ERROR_USUARIO_NO_AMIGO
    daoUsuario.eliminarAmigo(r, idUsuario, idUsuarioAmigo)
    daoUsuario.eliminarAmigo(r, idUsuarioAmigo, idUsuario)
    return erroresHTTP.OK


# Funciones para recomendador
def esFavorito(r, idUsuario, idAudio):
    if(idAudio in getAudiosFavoritos(r, idUsuario)):
        return 1
    return 0

def estaGuardado(r, idUsuario, idAudio):
    listas = daoUsuario.getListas(r, idUsuario)
    for idLista in listas:
        if(daoListas.getTipoLista(r, idLista) != constantes.LISTA_TIPO_FAVORITOS):
            if(idAudio in daoListas.getAudiosLista(r, idLista)):
                return 1
    return 0

def estaSuscrito(r, idUsuario, idArtista):
    artistas = daoUsuario.getArtistas(r, idUsuario)
    if(idArtista in artistas):
        return 1
    return 0

def getNFavoritosPorGenero(r, idUsuario):
    nFavoritos = [0]*constantes.GENERO_NUMERO_GENEROS

    for idAudio in getAudiosFavoritos(r, idUsuario):
        idGenero = daoAudios.obtenerGeneroCancion(r, idAudio)
        nFavoritos[idGenero] += 1

    return nFavoritos

def getNFavoritosPorArtista(r, idUsuario, idArtista):
    n = 0
    for idAudio in getAudiosFavoritos(r, idUsuario):
        if(idAudio in daoUsuario.getCanciones(r, idArtista)):
            n = n + 1
    return n

def getNFavoritos(r ,idUsuario):
    return len(getAudiosFavoritos(r, idUsuario))

def getAmigos(r, idUsuario):
    return daoUsuario.getAmigos(r, idUsuario)

def getAudiosFavoritos(r, idUsuario):
    listas = daoUsuario.getListas(r, idUsuario)
    audios = []
    for idLista in listas:
        if(daoListas.getTipoLista(r, idLista) == constantes.LISTA_TIPO_FAVORITOS):
            audios = daoListas.getAudiosLista(r, idLista)
    return audios





