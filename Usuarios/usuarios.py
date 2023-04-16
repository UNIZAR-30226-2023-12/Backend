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
        return erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS
    
    if(daoUsuario.existeEmailId(r, usuarioDiccionario[constantes.CLAVE_EMAIL])):
        return erroresHTTP.ERROR_USUARIO_EMAIL_YA_EXISTE

    # Si el usuario es administrador lo añadimos a la lista de administradores
    if(usuarioDiccionario[constantes.CLAVE_TIPO_USUARIO] == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.anyadirAdministrador(r, id)
        
    # Guardamos el usuario en la base de datos    
    daoUsuario.setUsuario(r, usuarioDiccionario)

    # Lo añadimos al hash con la clave como email y el valor como id
    daoUsuario.setEmailId(r, usuarioDiccionario[constantes.CLAVE_EMAIL], id)
    return erroresHTTP.OK

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

def getListasUsr(r, idUsuario):
    return daoUsuario.getListas(r, idUsuario)

def getSongsArtist(r, idArtista):
    if(r.exists(idArtista) == 0):
        return -1
    return daoUsuario.getCanciones(r, idArtista)

def getListaRepUsr(r, idLista):
    return daoListas.getLista(r, idLista)

def removeSongLista(r, idUsuario, idLista, idAudio):
    if (daoListas.existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    
    daoListas.eliminarAudioLista(r, idLista, idAudio)
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
            if(idAudio in daoListas.getAudios(r, idLista)):
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
            audios = daoListas.getAudios(r, idLista)
    return audios



