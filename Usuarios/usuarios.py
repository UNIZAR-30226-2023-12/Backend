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

def existeUsuarioEmail(r, email):
    return daoUsuario.existeEmailId(r, email)

def correctoDiccionarioUsuario(diccionario):
    if(sorted(diccionario.keys()) != sorted(daoUsuario.listaClaves)):
        return False
    return True

def correctoDiccionarioLista(diccionario):
    if(sorted(diccionario.keys()) != sorted(daoListas.listaClaves)):
        return False
    return True

def correctoDiccionarioCarpeta(diccionario):
    if(sorted(diccionario.keys()) != sorted(daoCarpetas.listaClaves)):
        return False
    return True


def tipoUsuarioValido(tipoUsuario):
    return daoUsuario.tipoUsuarioValido(tipoUsuario)

def getTipoUser(r, id):
    return daoUsuario.getTipoUsuario(r, id)

def getTipoNotificacion(r, id):
    return daoNotificaciones.getTipoNotificacion(r, id)

def isCarpetaPublica(r, id):
    return daoCarpetas.getPrivacidadCarpeta(r, id) == constantes.CARPETA_PUBLICA

def isListaPublica(r, id):
    return daoListas.getPrivacidadLista(r, id) == constantes.LISTA_PUBLICA

def getUsuarioEmisorNotificacion(r, id):
    return daoNotificaciones.getIdUsuarioEmisor(r, id)

def tipoListaValido(tipoLista):
    return daoListas.tipoListaValido(tipoLista)

def listaPrivacidadValida(privacidad):
    if(privacidad == constantes.LISTA_PRIVADA or privacidad == constantes.LISTA_PUBLICA):
        return True
    return False

def carpetaPrivacidadValida(privacidad):
    if(privacidad == constantes.CARPETA_PRIVADA or privacidad == constantes.CARPETA_PUBLICA):
        return True
    return False

def setUser(r, usuarioDiccionario):
    id = daoUsuario.getIdContador(r)
    usuarioDiccionario[constantes.CLAVE_ID_USUARIO] = id

    # Si el usuario es administrador lo añadimos a la lista de administradores
    if(usuarioDiccionario[constantes.CLAVE_TIPO_USUARIO] == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.anyadirAdministrador(r, id)
        
    # Guardamos el usuario en la base de datos    
    daoUsuario.setUsuario(r, usuarioDiccionario)

    # Lo añadimos al hash con la clave como email y el valor como id
    daoUsuario.setEmailId(r, usuarioDiccionario[constantes.CLAVE_EMAIL], id)
    return id


def getUser(r, id):
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
    idNotificacion = daoNotificaciones.getIdContador(r)
    diccionarioNotificaciones = {constantes.CLAVE_ID_NOTIFICACION: idNotificacion, 
                                 constantes.CLAVE_ID_USUARIO_EMISIOR: idUsuario, 
                                 constantes.CLAVE_TIPO_NOTIFICACION: constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA,
                                 constantes.CLAVE_TITULO_NOTIFICACION: constantes.TITULO_NOTIFICACION_ARTISTA,
                                 constantes.CLAVE_MENSAJE_NOTIFICACION: daoUsuario.getAlias(r,idUsuario) + constantes.MENSAJE_NOTIFICACION_ARTISTA}
    daoNotificaciones.setNotificacion(r, diccionarioNotificaciones)
    administradores = daoUsuario.getAdministradores(r)
    for admin in administradores:
        daoUsuario.anyadirNotificacion(r, admin, idNotificacion)
    
def ValidateUser(r, id, contrasenya):
    if (daoUsuario.getContrasenya(r, id) == contrasenya):
        return True
    return False

def getIdEmailId(r, email):
    return daoUsuario.getIdEmailId(r, email)
   

def setLastSecondHeared(r, idUsuario, idAudio, segundo):
    # Ponemos que el ultimo audio escuchado es el que nos pasan
    daoUsuario.setUltimoAudio(r, idUsuario, idAudio)
    # Creamos el clave valor con el id del audio y el usuario, el segundo como valor
    daoUsuario.setSegundosAudio(r, idUsuario, idAudio, segundo)

def getLastSecondHeared(r, idUsuario, idAudio):
    segundo = daoUsuario.getSegundosAudio(r, idUsuario, idAudio)

    # En caso de que no exista devolvemos que va por el segundo 0
    if (segundo == None):
        return 0
    return segundo

def subscribeToArtist(r, idUsuario, idArtista):
    daoUsuario.anyadirArtista(r, idUsuario, idArtista)

def unsubscribeToArtist(r, idUsuario, idArtista):
    daoUsuario.eliminarArtista(r, idUsuario, idArtista)

def getNotificationsUsr(r, idUsuario):
    return daoUsuario.getNotificaciones(r, idUsuario)

def getNotification(r, idNotificacion):
    return daoNotificaciones.getNotificacion(r, idNotificacion)

def removeNotification(r, idUsuario, idNotificacion):
    daoUsuario.eliminarNotificacion(r, idUsuario, idNotificacion)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)

# Funciones adicionales de artistas


# Funciones adcionales de administradores
def acceptArtist(r, idNotificacion):
    idUsuario = daoNotificaciones.getIdUsuarioEmisor(r, idNotificacion)
    
    # Eliminamos la notificación a los administradores
    administradores = daoUsuario.getAdministradores(r)
    for admin in administradores:
        daoUsuario.eliminarNotificacion(r, admin, idNotificacion)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)
    daoUsuario.setTipoUsuario(r, idUsuario, daoUsuario.constantes.USUARIO_ARTISTA)

def esAdministrador(r, id):
    if (r.exists(id) == 0):
        return False
    return daoUsuario.getTipoUsuario(r, id) == constantes.USUARIO_ADMINISTRADOR


# Funciones de listas de reproducción
def setLista(r, idUsuario, diccionarioLista):
    id = daoListas.getIdContador(r)
    diccionarioLista[constantes.CLAVE_ID_LISTA] = id

    daoListas.setLista(r, diccionarioLista) 
    daoUsuario.anyadirLista(r, idUsuario, id)
    return erroresHTTP.OK

def isListaFromUser(r, idUsuario, idLista):
    if (r.exists(idUsuario) == 0 or r.exists(idLista) == 0):
        return False
    listas = daoUsuario.getListas(r, idUsuario)
    if(idLista not in listas):
        return False
    return True

def isCarpetaFromUser(r, idUsuario, idCarpeta):
    if (r.exists(idUsuario) == 0 or r.exists(idCarpeta) == 0):
        return False
    carpetas = daoUsuario.getCarpetas(r, idUsuario)
    if(idCarpeta not in carpetas):
        return False
    return True

def isListaFromUser(r, idUsuario, idLista):
    if (r.exists(idUsuario) == 0 or r.exists(idLista) == 0):
        return False
    listas = daoUsuario.getListas(r, idUsuario)
    listas.append(daoCarpetas.getListasCarpeta(r, idUsuario))
    
    if(idLista not in listas):
        return False
    return True

def isAudioFromLista(r, idLista, idAudio):
    if (r.exists(idLista) == 0 or r.exists(idAudio) == 0):
        return False
    audios = daoListas.getAudiosLista(r, idLista)
    if(idAudio not in audios):
        return False
    return True

def isListaFromCarpeta(r, idCarpeta, idLista):
    if (r.exists(idCarpeta) == 0 or r.exists(idLista) == 0):
        return False
    listas = daoCarpetas.getListasCarpeta(r, idCarpeta)
    if(idLista not in listas):
        return False
    return True

def isNotificactionFromUser(r, idUsuario, idNotificacion):
    if (r.exists(idUsuario) == 0 or r.exists(idNotificacion) == 0):
        return False
    notificaciones = daoUsuario.getNotificaciones(r, idUsuario)
    if(idNotificacion not in notificaciones):
        return False
    return True

def setNombreLista(r, idLista, nombre):
    daoListas.setNombreLista(r, idLista, nombre)

def setSongLista(r, idLista, idAudio):
    daoListas.anyadirAudioLista(r, idLista, idAudio)

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
    return daoListas.getLista(r, idLista)

def getListasUsr(r, idUsuario):
    return daoUsuario.getListas(r, idUsuario)

def getListasUsrPublicas(r, idUsuario):
    listas = getListasUsr(r, idUsuario)
    listasPublicas = []
    for lista in listas:
        if(isListaPublica(r, lista)):
            listasPublicas.append(lista)

    return listasPublicas

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
    daoCarpetas.setCarpeta(r, diccionarioCarpeta) 
    daoUsuario.anyadirCarpeta(r, idUsuario, id)
    return erroresHTTP.OK

def addListToFolder(r, idCarpeta, idLista):
    daoCarpetas.anyadirListaCarpeta(r, idCarpeta, idLista)

def removeListFromFolder(r, idCarpeta, idLista):
    daoCarpetas.eliminarListaCarpeta(r, idCarpeta, idLista)
    
def removeFolder(r, idUsuario, idCarpeta):
    daoCarpetas.eliminarCarpeta(r, idCarpeta)
    daoUsuario.eliminarCarpeta(r, idUsuario, idCarpeta)
    

def getFolder(r, idCarpeta):
    return daoCarpetas.getCarpeta(r, idCarpeta)

def getListasFolder(r, idCarpeta):
    return daoCarpetas.getListasCarpeta(r, idCarpeta)

def getFoldersUser(r, idUsuario):
    return daoUsuario.getCarpetas(r, idUsuario)

def getPublicFoldersUser(r, idUsuario):
    folders = getFoldersUser(r, idUsuario)
    for folder in folders:
        if(daoCarpetas.getPrivacidadCarpeta(r, folder) == constantes.CARPETA_PRIVADA):
            folders.remove(folder)
    return folders

# Funciones para gestionar amigos
def isFriend(r, idUsuario, idUsuarioAmigo):
    if(idUsuario in daoUsuario.getAmigos(r, idUsuarioAmigo)):
        return True
    return False

def askFriend(r, idUsuario, idUsuarioAmigo):
    idNotificacion = daoNotificaciones.getIdContador(r)
    diccionarioNotificacion = {constantes.CLAVE_ID_NOTIFICACION: idNotificacion,
                               constantes.CLAVE_ID_USUARIO_EMISIOR: idUsuario,
                               constantes.CLAVE_TIPO_NOTIFICACION: constantes.NOTIFICACION_TIPO_AMIGO,
                               constantes.CLAVE_TITULO_NOTIFICACION: "Solicitud de amistad",
                               constantes.CLAVE_MENSAJE_NOTIFICACION: "El usuario " + daoUsuario.getAlias(r, idUsuario) + " quiere ser tu amigo"} 
    daoNotificaciones.setNotificacion(r, diccionarioNotificacion)
    daoUsuario.anyadirNotificacion(r, idUsuarioAmigo, idNotificacion)
    return erroresHTTP.OK

def acceptFriend(r, idUsuario, idNotificacion):
    idUsuarioAmigo = daoNotificaciones.getIdUsuarioEmisor(r, idNotificacion)    
    daoUsuario.anyadirAmigo(r, idUsuarioAmigo, idUsuario)
    daoUsuario.anyadirAmigo(r, idUsuario, idUsuarioAmigo)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)
    daoUsuario.eliminarNotificacion(r, idUsuario, idNotificacion)
    return erroresHTTP.OK

def getFriends(r, idUsuario):
    return daoUsuario.getAmigos(r, idUsuario)


def removeFriend(r, idUsuario, idUsuarioAmigo):
    daoUsuario.eliminarAmigo(r, idUsuario, idUsuarioAmigo)
    daoUsuario.eliminarAmigo(r, idUsuarioAmigo, idUsuario)


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

def isSubscribedToArtist(r, idUsuario, idArtista):
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





