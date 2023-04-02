# Módulo usuarios, con funciones de alto nivel para la api
import redis
import DAOS.daoListas as daoListas
import DAOS.daoUsuario as daoUsuario
import Configuracion.constantesPrefijosClaves as constantes

# Funciones de usuarios normales
def setUser(r, usuarioDiccionario):
    id = daoUsuario.getIdContador(r)
    usuarioDiccionario.add(constantes.CLAVE_ID_USUARIO, id)
    return daoUsuario.setUsuario(r, usuarioDiccionario)

def removeUser(r, id, contrasenya):
    if(daoUsuario.getContrasenya(r, id) != contrasenya):
        return -1
    amigos = daoUsuario.getAmigos(r, id)
    #Eliminar usuario de la lista de amigos de sus amigos
    for amigo in amigos:
        daoUsuario.eliminarAmigo(r, amigo, id)

    #Eliminar los sets de amigos, artistas y listas del usuario
    r.delete(daoUsuario.CLAVE_AMIGOS + id)
    r.delete(daoUsuario.CLAVE_ARTISTAS + id)
    r.delete(daoUsuario.CLAVE_LISTAS + id)
    return daoUsuario.eliminarUsuario(r, id)

def AskAdminToBeArtist(r, id, contrasenya):
    return 0
    
def ValidateUser(r, id, contrasenya):
    return daoUsuario.getContrasenya(r, id) == contrasenya

def getUser(r, id):
    usuario = daoUsuario.getUsuario(r, id)
    if(usuario == -1):
        #El usuario era un artista que ha sido eliminado
        daoUsuario.eliminarArtista(r, id)
        return -1
    return usuario



# Funciones adicionales de artistas


# Funciones adcionales de administradores
def acceptArtist(r, idUsario):
    return daoUsuario.setTipoUsuario(r, id, daoUsuario.constantes.USUARIO_ARTISTA)


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
    return daoUsuario.obtenerCanciones(r, idArtista)

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
