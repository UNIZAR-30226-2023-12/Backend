# Módulo usuarios, con funciones de alto nivel para la api
import redis
import DAOS.daoListas as daoListas
import DAOS.daoUsuario as daoUsuario
import Configuracion.constantesPrefijosClaves as constantes

# Funciones de usuarios normales
def setUser(r, usuarioDiccionario):
    id = daoUsuario.getIdContador(r)
    usuarioDiccionario.add(constantes.CLAVE_ID_USUARIO, id)
    return daoUsuario.guardarUsuario(r, usuarioDiccionario)

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
    return daoUsuario.obtenerContrasenya(r, id) == contrasenya

def getUser(r, id):
    usuario = daoUsuario.obtenerUsuario(r, id)
    if(usuario == -1):
        #El usuario era un artista que ha sido eliminado
        daoUsuario.desuscribirArtista(r, id)
        return -1
    return usuario



# Funciones adicionales de artistas


# Funciones adcionales de administradores
def acceptArtist(r, idUsario):
    return daoUsuario.cambiarTipoUsuario(r, id, daoUsuario.constantesPrefijosClaves.USUARIO_ARTISTA)


# Funciones de listas de repro
def setSongLista(r, idUsuario, idLista, idAudio):
    if (r.exists(idUsuario) == 0 or r.exists(idAudio) == 0 or r.exists(idLista) == 0):
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
    return daoUsuario.obtenerListas(r, idUsuario)

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
