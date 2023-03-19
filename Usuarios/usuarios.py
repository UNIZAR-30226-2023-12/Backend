# Módulo usuarios, con funciones de alto nivel para la api
import redis
import daoUsuario

def setUser(r, usuarioDiccionario):
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
    if(daoUsuario.obtenerContrasenya(r, id) != contrasenya):
        return -1
    return daoUsuario.cambiarTipoUsuario(r, id, daoUsuario.USUARIO_ARTISTA)
    
def ValidateUser(r, id, contrasenya):
    return daoUsuario.obtenerContrasenya(r, id) == contrasenya

def getUser(r, id):
    usuario = daoUsuario.obtenerUsuario(r, id)
    if(usuario == -1):
        #El usuario era un artista que ha sido eliminado
        daoUsuario.desuscribirArtistas(r, id)
        return -1
    return usuario

