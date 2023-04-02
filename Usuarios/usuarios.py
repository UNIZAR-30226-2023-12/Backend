# Módulo usuarios, con funciones de alto nivel para la api
import redis
import DAOS.daoListas as daoListas
import DAOS.daoUsuario as daoUsuario
import DAOS.daoNotificaciones as daoNotificaciones
import Configuracion.constantesPrefijosClaves as constantes

# Funciones de usuarios normales
def setUser(r, usuarioDiccionario):
    id = daoUsuario.getIdContador(r)
    usuarioDiccionario.add(constantes.CLAVE_ID_USUARIO, id)
    # Si el usuario es administrador lo añadimos a la lista de administradores
    if(usuarioDiccionario[constantes.CLAVE_TIPO_USUARIO] == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.anyadirAdministrador(r, id)
    daoUsuario.setUsuario(r, usuarioDiccionario)
    return 1

def removeUser(r, id, contrasenya):
    if(r.exists(id) == 0):
        return -1
    amigos = daoUsuario.getAmigos(r, id)
    #Eliminar usuario de la lista de amigos de sus amigos
    for amigo in amigos:
        daoUsuario.eliminarAmigo(r, amigo, id)

    #Eliminar los sets de amigos, artistas y listas del usuario
    r.delete(constantes.CLAVE_AMIGOS + id)
    r.delete(constantes.CLAVE_ARTISTAS + id)
    r.delete(constantes.CLAVE_LISTAS + id)

    #Si es administrador, eliminarlo de la lista de administradores
    if(daoUsuario.getTipoUsuario(r, id) == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.eliminarAdministrador(r, id)
    daoUsuario.eliminarUsuario(r, id)
    return 1

def AskAdminToBeArtist(r, idUsuario):
    if(r.exists(idUsuario) == 0):
        return -2
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
    return 1
    
def ValidateUser(r, id, contrasenya):
    if (r.exists(id) == 0):
        return -2
    if (daoUsuario.getContrasenya(r, id) == contrasenya):
        return 1
    return -1

def getUser(r, id):
    usuario = daoUsuario.getUsuario(r, id)
    if(usuario == -1):
        #El usuario era un artista que ha sido eliminado
        daoUsuario.eliminarArtista(r, id)
        return -1
    return usuario



# Funciones adicionales de artistas


# Funciones adcionales de administradores
def acceptArtist(r, idUsuario, idNotificacion):
    administradores = daoUsuario.getAdministradores(r)
    if(daoNotificaciones.getIdUsuarioEmisor(r, idNotificacion) != idUsuario):
        return -1
    if(daoNotificaciones.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA):
        return -1
    
    # Eliminamos la notificación a los administradores
    for admin in administradores:
        daoUsuario.eliminarNotificacion(r, admin, idNotificacion)
    
    return daoUsuario.setTipoUsuario(r, idUsuario, daoUsuario.constantes.USUARIO_ARTISTA)


# Funciones de listas de reproducción
def setLista(r, idUsuario, diccionarioLista):
    if (r.exists(idUsuario) == 0):
        return -1
    id = daoListas.getIdContador(r)
    diccionarioLista.add(constantes.CLAVE_ID_LISTA, id)
    return daoListas.crearPlaylist(r, diccionarioLista) 

def setSongLista(r, idLista, idAudio):
    if (r.exists(idAudio) == 0):
        return -3
    if (r.exists(idLista) == 0):
        return -1
    return daoListas.anadirCancionPlaylist(r, idLista, idAudio)

def setPrivacyLista(r, idUsuario, idLista, publica):
    if (r.exists(idUsuario) == 0):
        return -2
    if (r.exists(idLista) == 0):
        return -1
    daoListas.cambiarPublicaPlaylist(r, idLista, publica)
    return 1

def removListaRepUsr(r, idUsuario, idLista):
    if (r.exists(idUsuario) == 0):
        return -2
    if (r.exists(idLista) == 0):
        return -1
    daoListas.eliminarPlaylist(r, idLista)
    daoUsuario.eliminarLista(r, idUsuario, idLista)
    return 1

def getListasUsr(r, idUsuario):
    return daoUsuario.getListas(r, idUsuario)

def getSongsArtist(r, idArtista):
    if(r.exists(idArtista) == 0):
        return -1
    return daoUsuario.getCanciones(r, idArtista)

def getListaRepUsr(r, idLista):
    return daoListas.obtenerPlaylist(r, idLista)

def removeSongLista(r, idUsuario, idLista, idAudio):
    if(r.exists(idUsuario) == 0):
        return -2
    if(r.exists(idLista) == 0):
        return -1
    return daoListas.eliminarCancionPlaylist(r, idLista, idAudio)

def changeNameListRepUsr(r, idLista, nombre):
    return daoListas.cambiarNombrePlaylist(r, idLista, nombre)
