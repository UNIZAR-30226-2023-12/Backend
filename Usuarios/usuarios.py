# Módulo usuarios, con funciones de alto nivel para la api
import redis
import DAOS.daoListas as daoListas
import DAOS.daoUsuario as daoUsuario
import DAOS.daoNotificaciones as daoNotificaciones
import DAOS.daoCarpetas as daoCarpetas
import DAOS.daoAudio as daoAudios
import Configuracion.constantesPrefijosClaves as constantes
import Configuracion.constantesErroresHTTP as erroresHTTP
from cryptography.fernet import Fernet


key = Fernet.generate_key()
f = Fernet(key)
##############################################################################################################
## Funciones usuarios Normales
##############################################################################################################
def existeUsuario(r, id):
    return daoUsuario.existeUsuario(r, id)

# Devuelve True si ya existe un usuario con ese email
def existeUsuarioEmail(r, email):
    return daoUsuario.existeEmailId(r, email)

# Devuelve True si el diccionar que se pasa como parámetro tiene todos los campos necesarios para crear un usuario
def correctoDiccionarioUsuario(diccionario):
    if(sorted(diccionario.keys()) != sorted(daoUsuario.listaClaves)):
        return False
    return True

# Devuelve true si el tipoUsuario que se pasa como parámetro es válido(tipoNormal, tipoAdministrador, etc.)
def tipoUsuarioValido(tipoUsuario):
    return daoUsuario.tipoUsuarioValido(tipoUsuario)

# Crea un usuario en la base de datos a partir de un diccionario con los datos del usuario
def setUser(r, usuarioDiccionario):
    id = daoUsuario.getIdContador(r)
    usuarioDiccionario[constantes.CLAVE_ID_USUARIO] = id

    # Si el usuario es administrador lo añadimos a la lista de administradores
    if(usuarioDiccionario[constantes.CLAVE_TIPO_USUARIO] == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.anyadirAdministrador(r, id)
            
    daoUsuario.setUsuario(r, usuarioDiccionario)

    # Lo añadimos al hash con la clave como email y el valor como id
    daoUsuario.setEmailId(r, usuarioDiccionario[constantes.CLAVE_EMAIL], id)
    return id

def getUser(r, id):
    return daoUsuario.getUsuario(r, id)

# Devuelve la información pública de un usuario
def getUserPublicData(r, id ):
    user = getUser(r, id)
    del user[constantes.CLAVE_CONTRASENYA]
    del user[constantes.CLAVE_EMAIL]
    return user

def setContrasenya(r, id, contrasenya):
    daoUsuario.setContrasenya(r, id, contrasenya)

# Devuelve el id del usuario a partir de su email
def getIdEmailId(r, email):
    return daoUsuario.getIdEmailId(r, email)
   
# Guarda en la base de datos los segundos que ha escuchado un usuario de un audio
def setLastSecondHeared(r, idUsuario, idAudio, segundo):
    # Ponemos que el ultimo audio escuchado es el que nos pasan
    daoUsuario.setUltimoAudio(r, idUsuario, idAudio)
    # Creamos el clave valor con el id del audio y el usuario, el segundo como valor
    daoUsuario.setSegundosAudio(r, idUsuario, idAudio, segundo)

# Devuelve el segundo por el que va el usuario en un audio
def getLastSecondHeared(r, idUsuario, idAudio):
    segundo = daoUsuario.getSegundosAudio(r, idUsuario, idAudio)

    # En caso de que no exista devolvemos que va por el segundo 0
    if (segundo == None):
        return 0
    return segundo

# Gets y Sets de usuarios
def getEmailUsr(r, idUsuario):
    return daoUsuario.getEmail(r, idUsuario)

def setEmailUsr(r, idUsuario, email):
    daoUsuario.eliminarEmailId(r, daoUsuario.getEmail(r, idUsuario))
    daoUsuario.setEmailId(r, email, idUsuario)
    daoUsuario.setEmail(r, idUsuario, email)

def getAliasUsr(r, idUsuario):
    return daoUsuario.getAlias(r, idUsuario)

def setAliasUsr(r, idUsuario, alias):
    daoUsuario.setAlias(r, idUsuario, alias)

def getContrasenyaUsr(r, idUsuario):
    return daoUsuario.getContrasenya(r, idUsuario)

def setContrasenyaUsr(r, idUsuario, contrasenya):
    daoUsuario.setContrasenya(r, idUsuario, contrasenya)

def getTipoUsr(r, id):
    return daoUsuario.getTipoUsuario(r, id)

def setTipoUsr(r, idUsuario, tipo):
    daoUsuario.setTipoUsuario(r, idUsuario, tipo)

def getImagenPerfilUsr(r, idUsuario):
    imagen = daoUsuario.getImagenPerfil(r, idUsuario)
    if(imagen == None):
        return daoUsuario.getImagenPerfilDefault(r)
    return imagen

def setImagenPerfilUsr(r, idUsuario, imagen):
    daoUsuario.setImagenPerfil(r, idUsuario, imagen)

def setCalidadPorDefecto(r, idUsuario, calidad):
    daoUsuario.setCalidadPorDefecto(r, idUsuario, calidad)

def getCalidadPorDefecto(r, idUsuario):
    return daoUsuario.getCalidadPorDefecto(r, idUsuario)

# Elimina el usuario de la base de datos, tener en cuenta 
# que el usuario en caso de ser artista no se borra de sus suscriptores
def removeUser(r, id):
    amigos = daoUsuario.getAmigos(r, id)
    # Eliminar usuario de la lista de amigos de sus amigos
    for amigo in amigos:
        daoUsuario.eliminarAmigo(r, amigo, id)
    # Elimina las listas del usuario
    for lista in daoUsuario.getListas(r, id):
        removeLista(r, id, lista)
    # Elimina las carpetas del usuario
    for folder in daoUsuario.getCarpetas(r, id):
        removeFolder(r, id, folder)
    
        #Eliminar los sets de amigos, artistas, listas, notificaciones y carpetas

    r.delete(constantes.PREFIJO_AMIGOS + id)
    r.delete(constantes.PREFIJO_ARTISTAS_SUSCRITOS + id)
    r.delete(constantes.CLAVE_LISTAS + id)
    r.delete(constantes.PREFIJO_NOTIFICACIONES + id)
    r.delete(constantes.PREFIJO_CARPETAS + id)

    daoUsuario.eliminarEmailId(r, daoUsuario.getEmail(r, id))

    #Si es administrador, eliminarlo de la lista de administradores
    if(daoUsuario.getTipoUsuario(r, id) == constantes.USUARIO_ADMINISTRADOR):
        daoUsuario.eliminarAdministrador(r, id)
    #Eliminar la información del usuario
    daoUsuario.eliminarUsuario(r, id)

# Función para solictiar ser artista a los administradores
def AskAdminToBeArtist(r, idUsuario, mensajeNotificacion):
    idNotificacion = daoNotificaciones.getIdContador(r)
    diccionarioNotificaciones = {constantes.CLAVE_ID_NOTIFICACION: idNotificacion, 
                                 constantes.CLAVE_ID_USUARIO_EMISIOR: idUsuario, 
                                 constantes.CLAVE_TIPO_NOTIFICACION: constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA,
                                 constantes.CLAVE_TITULO_NOTIFICACION: constantes.TITULO_NOTIFICACION_ARTISTA,
                                 constantes.CLAVE_MENSAJE_NOTIFICACION: mensajeNotificacion}
    daoNotificaciones.setNotificacion(r, diccionarioNotificaciones)
    # Añadimos la notificación a todos los administradores
    for admin in  daoUsuario.getAdministradores(r):
        daoUsuario.anyadirNotificacion(r, admin, idNotificacion)

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

def rejectFriend(r, idUsuario, idNotificacion):
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)
    daoUsuario.eliminarNotificacion(r, idUsuario, idNotificacion)
    return erroresHTTP.OK

def getFriends(r, idUsuario):
    return daoUsuario.getAmigos(r, idUsuario)


def removeFriend(r, idUsuario, idUsuarioAmigo):
    daoUsuario.eliminarAmigo(r, idUsuario, idUsuarioAmigo)
    daoUsuario.eliminarAmigo(r, idUsuarioAmigo, idUsuario)

# Devuelve True si la contraseña dado un usuario es correcta, False en caso contrario
def ValidateUser(r, id, contrasenya):
    if (daoUsuario.getContrasenya(r, id) == contrasenya):
        return True
    return False

def subscribeToArtist(r, idUsuario, idArtista):
    daoUsuario.anyadirArtista(r, idUsuario, idArtista)

def unsubscribeToArtist(r, idUsuario, idArtista):
    daoUsuario.eliminarArtista(r, idUsuario, idArtista)

def getSubscriptionsUsr(r, idUsuario):
    return daoUsuario.getArtistas(r, idUsuario)

##############################################################################################################
## Funciones Usuarios Artista
##############################################################################################################

def anyadirCancionArtista(r, idArtista, idCancion):
    daoUsuario.anyadirCancion(r, idArtista, idCancion)

def eliminarCancionArtista(r, idArtista, idCancion):
    daoUsuario.eliminarCancion(r, idArtista, idCancion)

def getCancionesArtista(r, idArtista):
    return daoUsuario.getCanciones(r, idArtista)


##############################################################################################################
## Funciones Usuarios Administradores
##############################################################################################################

def esAdministrador(r, id):
    if (r.exists(id) == 0):
        return False
    return daoUsuario.getTipoUsuario(r, id) == constantes.USUARIO_ADMINISTRADOR

def acceptArtist(r, idNotificacion):
    idUsuario = daoNotificaciones.getIdUsuarioEmisor(r, idNotificacion)
    
    # Eliminamos la notificación a los administradores
    administradores = daoUsuario.getAdministradores(r)
    for admin in administradores:
        daoUsuario.eliminarNotificacion(r, admin, idNotificacion)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)
    daoUsuario.setTipoUsuario(r, idUsuario, daoUsuario.constantes.USUARIO_ARTISTA)

def rejectArtist(r, idNotificacion):
    # Eliminamos la notificación a los administradores
    administradores = daoUsuario.getAdministradores(r)
    for admin in administradores:
        daoUsuario.eliminarNotificacion(r, admin, idNotificacion)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)

##############################################################################################################
## Funciones Notificaciones
##############################################################################################################
def existeNotificacion(r, id):
    return daoNotificaciones.existeNotificacion(r, id)

def getTipoNotificacion(r, id):
    return daoNotificaciones.getTipoNotificacion(r, id)

# Devuelve el id del usuario emisor de la notificación
def getUsuarioEmisorNotificacion(r, id):
    return daoNotificaciones.getIdUsuarioEmisor(r, id)

# Devuelve un set con los ids de las notificaciones de un usuario
def getNotificationsUsr(r, idUsuario):
    return daoUsuario.getNotificaciones(r, idUsuario)

def getNotification(r, idNotificacion):
    return daoNotificaciones.getNotificacion(r, idNotificacion)

def removeNotification(r, idUsuario, idNotificacion):
    daoUsuario.eliminarNotificacion(r, idUsuario, idNotificacion)
    daoNotificaciones.eliminarNotificacion(r, idNotificacion)


def isNotificactionFromUser(r, idUsuario, idNotificacion):
    if (r.exists(idUsuario) == 0 or r.exists(idNotificacion) == 0):
        return False
    notificaciones = daoUsuario.getNotificaciones(r, idUsuario)
    if(idNotificacion not in notificaciones):
        return False
    return True

def anyadirNotificacionSubidaCancion(r, idArtista, idCancion):
    subs = daoUsuario.getSubscriptores(r, idArtista)
    idNotificacion = daoNotificaciones.getIdContador(r)
    for sub in subs:
        diccionarioNotificacion = {constantes.CLAVE_ID_NOTIFICACION: idNotificacion,
                                   constantes.CLAVE_TIPO_NOTIFICACION: constantes.NOTIFCACION_TIPO_NORMAL,
                                   constantes.CLAVE_ID_USUARIO_EMISIOR: idArtista,
                                   constantes.CLAVE_TITULO_NOTIFICACION: "Nueva canción del artista ", 
                                   constantes.CLAVE_MENSAJE_NOTIFICACION : "La cancion del aritsta "+ daoUsuario.getAlias(r, idArtista) + 
                                   " llamada" + daoAudios.obtenerNombreCancion(r, idCancion) + " ha sido subida"}
        daoNotificaciones.setNotificacion(r, diccionarioNotificacion)
        daoUsuario.anyadirNotificacion(r, sub, idNotificacion)
        

##############################################################################################################
## Funciones Listas
##############################################################################################################
def existeLista(r, id):
    return daoListas.existeLista(r, id)

# Devuelve True si la lista es pública, False en caso contrario
def isListaPublica(r, id):
    return daoListas.getPrivacidadLista(r, id) == constantes.LISTA_PUBLICA

# Devuelve True si el diccionario que se pasa como parámetro tiene todos los campos necesarios para crear una lista
def correctoDiccionarioLista(diccionario):
    if(sorted(diccionario.keys()) != sorted(daoListas.listaClaves)):
        return False
    return True

# Devuelve true si el tipoLista que se pasa como parámetro es válido(tipoNormal, tipoSolitudAmistad, etc.)
def tipoListaValido(tipoLista):
    return daoListas.tipoListaValido(tipoLista)

# Devuelve True si la privacidad que se pasa como parámetro es válida
def isListaPrivacidadValida(privacidad):
    if(privacidad == constantes.LISTA_PRIVADA or privacidad == constantes.LISTA_PUBLICA):
        return True
    return False

# Devuelve True si la lista pertenece al usuario, False en caso contrario
def isListaFromUser(r, idUsuario, idLista):
    if (r.exists(idUsuario) == 0 or r.exists(idLista) == 0):
        return False
    listas = getAllListasUsr(r, idUsuario)
    if(idLista not in listas):
        return False
    return True

# Devuelve True si el audio pertenece a la lista, False en caso contrario
def isAudioFromLista(r, idLista, idAudio):
    if (r.exists(idLista) == 0 or r.exists(idAudio) == 0):
        return False
    audios = daoListas.getAudiosLista(r, idLista)
    if(idAudio not in audios):
        return False
    return True

# Devuelve True si la lista pertenece a la carpeta, False en caso contrario
def isListaFromCarpeta(r, idCarpeta, idLista):
    if (r.exists(idCarpeta) == 0 or r.exists(idLista) == 0):
        return False
    listas = daoCarpetas.getListasCarpeta(r, idCarpeta)
    if(idLista not in listas):
        return False
    return True

def setLista(r, idUsuario, diccionarioLista):
    id = daoListas.getIdContador(r)
    diccionarioLista[constantes.CLAVE_ID_LISTA] = id

    # Creamos la lista
    daoListas.setLista(r, diccionarioLista) 
    # Añadimos la lista al usuario
    daoUsuario.anyadirLista(r, idUsuario, id)

def getLista(r, idLista):   
    return daoListas.getLista(r, idLista)

# Gets y Sets de Listas de Reproduccion
def getNombreListaRep(r, idLista):
    return daoListas.getNombreLista(r, idLista)

def setNombreListaRep(r, idLista, nombre):
    daoListas.setNombreLista(r, idLista, nombre)

def getTipoListaRep(r, idLista):
    return daoListas.getTipoLista(r, idLista)

def setTipoListaRep(r, idLista, tipo):
    daoListas.setTipoLista(r, idLista, tipo)

def getPrivacidadListaRep(r, idLista):
    return daoListas.getPrivacidadLista(r, idLista)

def setPrivacidadListaRep(r, idLista, privacidad):
    daoListas.setPrivacidadLista(r, idLista, privacidad)

def getIDUsuarioListaRep(r, idLista):
    return daoListas.getIDUsuario(r, idLista)


# Devuelve un set con los ids de todas las listas del usuario menos las que se encuentran en una carpeta
def getListasUsr(r, idUsuario):
    listas = daoUsuario.getListas(r, idUsuario)
    return listas

# Devuelve un set con los ids de todas las listas del usuario, incluyendo carpetas
def getAllListasUsr(r, idUsuario):
    listas = daoUsuario.getListas(r, idUsuario)
    for carpeta in daoUsuario.getCarpetas(r, idUsuario):
        listas.extend(daoCarpetas.getListasCarpeta(r, carpeta))
    return listas

# Devuelve un set con los ids de todas las listas del usuario que son públicas
def getListasUsrPublicas(r, idUsuario):
    listas = getAllListasUsr(r, idUsuario)
    listasPublicas = []
    for lista in listas:
        if(isListaPublica(r, lista)):
            listasPublicas.append(lista)

    return listasPublicas

def anyadirAudioLista(r, idLista, idAudio):
    daoListas.anyadirAudioLista(r, idLista, idAudio)

def getAudiosLista(r, idLista):
    return daoListas.getAudiosLista(r, idLista)

def removeSongLista(r, idLista, idAudio):
    if (daoListas.existeLista(r, idLista) == False):
        return erroresHTTP.ERROR_LISTA_NO_ENCONTRADA
    
    if (daoAudios.existeCancion(r, idAudio) == False):
        return erroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    daoListas.eliminarAudioLista(r, idLista, idAudio)
    return erroresHTTP.OK

# Devuelve el link dado el id de una lista
def getLinkAudio(r, id):
    idBytes = bytes(id, 'utf-8')
    link = f.encrypt(idBytes)
    link = link.decode('utf-8')
    return link

# Devuelve el id de una lista dado el link
def getAudioFromLink(r, link):
    link = bytes(link, 'utf-8')
    id = f.decrypt(link)
    id = id.decode('utf-8')
    return id

def removeLista(r, idUsuario, idLista):
    # Elimino la lista de canciones de la playlist
    r.delete(constantes.CLAVE_AUDIOS + ":" + idLista)
    r.srem(constantes.CLAVE_LISTAS, idLista)

    # Elimino la infmoración de la lista
    daoListas.eliminarLista(r, idLista)

    # Elimino la el id de la lista de las listas del usuario
    if(idLista in daoUsuario.getListas(r, idUsuario)):
        daoUsuario.eliminarLista(r, idUsuario, idLista)
    
    # Elimino el id de la lista de las carpetas del usuario
    for idCarpeta in daoUsuario.getCarpetas(r, idUsuario):
        if(idLista in daoCarpetas.getListasCarpeta(r,idCarpeta)):
            daoCarpetas.eliminarListaCarpeta(r, idCarpeta, idLista)

##############################################################################################################
## Funciones carpetas
##############################################################################################################

def existeCarpeta(r, id):
    return daoCarpetas.existeCarpeta(r, id)

# Devuelve True si el diccionario que se pasa como parámetro tiene todos los campos necesarios para crear una carpeta
def correctoDiccionarioCarpeta(diccionario):
    if(sorted(diccionario.keys()) != sorted(daoCarpetas.listaClaves)):
        return False
    return True

# Devuelve True si la carpeta es pública, False en caso contrario
def isCarpetaPublica(r, id):
    return daoCarpetas.getPrivacidadCarpeta(r, id) == constantes.CARPETA_PUBLICA

# Devuelve true si la que se pasa como parámetro es válida
def carpetaPrivacidadValida(privacidad):
    if(privacidad == constantes.CARPETA_PRIVADA or privacidad == constantes.CARPETA_PUBLICA):
        return True
    return False

def isCarpetaFromUser(r, idUsuario, idCarpeta):
    if (r.exists(idUsuario) == 0 or r.exists(idCarpeta) == 0):
        return False
    carpetas = daoUsuario.getCarpetas(r, idUsuario)
    if(idCarpeta not in carpetas):
        return False
    return True


def setFolder(r, idUsuario, diccionarioCarpeta):
    id = daoCarpetas.getIdContador(r)
    diccionarioCarpeta[constantes.CLAVE_ID_CARPETA] = id
    daoCarpetas.setCarpeta(r, diccionarioCarpeta) 
    daoUsuario.anyadirCarpeta(r, idUsuario, id)
    return id

def getFolder(r, idCarpeta):
    return daoCarpetas.getCarpeta(r, idCarpeta)

# Gets y Sets de Carpeta
def getNombreCarpeta(r, idCarpeta):
    return daoCarpetas.getNombreCarpeta(r, idCarpeta)

def setNombreCarpeta(r, idCarpeta, nombre):
    daoCarpetas.setNombreCarpeta(r, idCarpeta, nombre)

def getPrivacidadCarpeta(r, idCarpeta):
    return daoCarpetas.getPrivacidadCarpeta(r, idCarpeta)

def setPrivacidadCarpeta(r, idCarpeta, privacidad):
    daoCarpetas.setPrivacidadCarpeta(r, idCarpeta, privacidad)

# Devuelve un set con los ids de todas las carpetas del usuario
def getFoldersUser(r, idUsuario):
    return daoUsuario.getCarpetas(r, idUsuario)

# Devuelve un set con los ids de todas las carpetas del usuario que son públicas
def getPublicFoldersUser(r, idUsuario):
    folders = getFoldersUser(r, idUsuario)
    for folder in folders:
        if(daoCarpetas.getPrivacidadCarpeta(r, folder) == constantes.CARPETA_PRIVADA):
            folders.remove(folder)
    return folders

def addListToFolder(r, idUsuario, idCarpeta, idLista):
    daoUsuario.eliminarLista(r, idUsuario, idLista)
    daoCarpetas.anyadirListaCarpeta(r, idCarpeta, idLista)

def getListasFolder(r, idCarpeta):
    return daoCarpetas.getListasCarpeta(r, idCarpeta)

def removeListFromFolder(r, idCarpeta, idLista):
    daoCarpetas.eliminarListaCarpeta(r, idCarpeta, idLista)

       
def removeFolder(r, idUsuario, idCarpeta):
    # Elimino las listas de la carpeta
    for lista in daoCarpetas.getListasCarpeta(r, idCarpeta):
        # Elimino las lista
        removeLista(r, idUsuario, lista)


    # Elimino la información de la carpeta
    daoCarpetas.eliminarCarpeta(r, idCarpeta)

    r.delete(constantes.CLAVE_LISTAS_CARPETA + ":" + idCarpeta)
    # Elimino el id de la carpeta del usuario
    daoUsuario.eliminarCarpeta(r, idUsuario, idCarpeta)
    
##############################################################################################################
# Funciones para recomendador
##############################################################################################################
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



def setCodigoRecuperacion(r, idUsuario, codigo):
    daoUsuario.setCodigoRecuperacion(r, idUsuario, codigo)

def getCodigoRecuperacion(r, idUsuario):
    return daoUsuario.getCodigoRecuperacion(r, idUsuario)
