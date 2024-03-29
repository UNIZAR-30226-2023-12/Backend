#########################################################################################
#
#
# MODULO DAO PARA LA GESTION DE AUDIOS
# Este modulo contiene las funciones necesarias para la gestion de los audios
# con el tratamiento de errores correspondiente
# Si se ha podido realizar la operación correctamente se devuelve 0, en caso contrario
# se devuelve -1
#
#
#########################################################################################

import redis
import Configuracion.constantesPrefijosClaves as constantes
import DAOS.daoUsuario as daoUsuario
import DAOS.daoListas as daoListas


#########################################################################################
#
#
# FUNCIONES PARA ALMACENAR/ACTUALIZAR CANCIONES
# Una cancion tiene los siguientes posibles atributos:
#   - id (clave para el hash)
#   - nombre
#   - artista
#   - calidad
#   - nVeces
#   - val
#   - generos
#   - ficheroAltaCalidad
#   - ficheroBajaCalidad
#   - longitud
#   - numFavoritos
#   - esPodcast
#
#
#########################################################################################

# Función para ver si existe una cancion con un id determinado
def existeCancion(r, id):
    if r.exists(id) == 0:
        return False
    else:
        return True

# Función para incrementar el id artificial y devolverlo de forma atómica
def incrementarIDUltimoAudio(r):
    id = r.incr('idUltimoAudio')
    return id

def incrementarReproduccion(r, id):
    id = r.incr('reproducciones:'+id)

def getReproducciones(r, id):
    return r.get('reproducciones:'+id)


# Funcion para guardar una cancion en la base de datos, modificada para trabajar con diccionarios
def guardarCancion(r, cancionDic):
    id = cancionDic['id']
    ficheroAltaCalidad = cancionDic['ficheroAltaCalidad']
    ficheroBajaCalidad = cancionDic['ficheroBajaCalidad']

    # Ahora quito el id del diccionario para que no se guarde en el hash
    del cancionDic['id']
    del cancionDic['ficheroAltaCalidad']
    del cancionDic['ficheroBajaCalidad']
    
    r.hset(id, 'nValoraciones', 0)
    r.set('reproducciones:'+id, 0)

    r.hmset(id, cancionDic)
    r.hmset(id+":ficheros", {'ficheroAltaCalidad': ficheroAltaCalidad, 
                            'ficheroBajaCalidad': ficheroBajaCalidad})

    r.sadd(constantes.PREFIJO_LISTA_GLOBAL_CANCIONES, id)

    return 0

# Funcion para cambiar el nombre de una cancion
def cambiarNombreCancion(r, id, nombre):
    r.hset(id, 'nombre', nombre)
    return 0

# Funcion para cambiar el artista de una cancion
def cambiarArtistaCancion(r, id, artista):
    r.hset(id, 'artista', artista)
    return 0

# Funcion para cambiar la calidad de una cancion
def cambiarCalidadCancion(r, id, calidad):
    r.hset(id, 'calidad', calidad)
    return 0

# Funcion para cambiar el num de veces que se ha escuchado una cancion
def cambiarVecesreproducidasCancion(r, id, nVeces):
    r.hset(id, 'nVeces', nVeces)
    return 0

# Funcion para cambiar la valoracion de una cancion
def cambiarValCancion(r, id, val):
    r.inc(id, 'nValoraciones')
    r.inc(id, 'val', int(val))

    return 0

# Funcion para cambiar el genero de una cancion
def cambiarGeneroCancion(r, id, genero):
    r.hset(id, 'generos', genero)
    return 0

# Funcion para cambiar el fichero de alta calidad de una cancion
def cambiarFicheroAltaCalidad(r, id, ficheroAltaCalidad):
    r.hset(id+":ficheros", 'ficheroAltaCalidad', ficheroAltaCalidad)
    return 0

# Funcion para cambiar el fichero de baja calidad de una cancion
def cambiarFicheroBajaCalidad(r, id, ficheroBajaCalidad):
    r.hset(id+":ficheros", 'ficheroBajaCalidad', ficheroBajaCalidad)     
    return 0

# Funcion para cambiar la longitud de una canción
def cambiarLongitudCancion(r, id, longitud):
    r.hset(id, 'longitud', longitud)    
    return 0

# Funcion para cambiar el numero de favoritos de una canción
def cambiarNumFavoritosCancion(r, id, numFavoritos):
    r.incrby(id, 'numFavoritos', numFavoritos)
    return 0

# Funcion para cambiar el atributo esPodcast de un audio
def cambiarEsPodcast(r, id, esPodcast):
    r.hset(id, 'esPodcast', esPodcast)
    return 0

def setImagen(r, id, imagen):
    r.hset(id, constantes.CLAVE_IMAGEN_AUDIO, imagen)
    return 0

# Funcion para eliminar una cancion
def eliminarCancion(r, id):
    r.delete(id)
    r.srem(constantes.PREFIJO_LISTA_GLOBAL_CANCIONES, id)
    return 0

def setLastSecondHeared(r, idUsuario, idAudio, second):
    r.set('lastSecondHeared:'+idUsuario+':'+idAudio, second)

#########################################################################################
#
#
# FUNCIONES PARA OBTENER CANCIONES Y SUS ATRIBUTOS POR SEPARADO
#
#
#########################################################################################

# Funcion para obtener una cancion
def obtenerCancion(r, id):
    datos_control = r.hgetall(id)
    datos_control['ficheroAltaCalidad'] = obtenerFicheroAltaCalidad(r, id)
    datos_control['ficheroBajaCalidad'] = obtenerFicheroBajaCalidad(r, id)

    return datos_control

# Devuelve los datos de control de un audio (sin los ficheros)
def obtenerDatosCancion(r, id):
    return r.hgetall(id)

def obtenerDatosCanciones(r, ids):
    datosCanciones = []

    for id in ids:
        datos = obtenerDatosCancion(r, id)
        datos[constantes.CLAVE_ID_AUDIO] = id
        datosCanciones.append(datos)

    return datosCanciones


    


def obtenerTodasLasCanciones(r):
    return r.smembers(constantes.PREFIJO_LISTA_GLOBAL_CANCIONES)

def buscarAudios(r, query):
    canciones = obtenerTodasLasCanciones(r)
    podcasts = obtenerTodosLosPodcasts(r)
    artistas = daoUsuario.obtenerTodosArtistas(r)
    listas = daoListas.obtenerTodasLasListas(r)

    datosCanciones = obtenerDatosCanciones(r, canciones)
    datosPodcasts = obtenerDatosPodcasts(r, podcasts)
    datosArtistas = daoUsuario.obtenerDatosArtistas(r, artistas)
    datosListas = daoListas.obtenerDatosListas(r, listas)
    encontradas = []
    artistasEncontrados = []
    listasEncontradas = []


    if len(datosCanciones) > 0:
        for audio in datosCanciones:
            if (query.lower() in audio[constantes.CLAVE_NOMBRE_AUDIO].lower() or 
                query.lower() in audio[constantes.CLAVE_ARTISTA_AUDIO].lower() or 
                query.lower() in constantes.obtenerNombreGenero(audio[constantes.CLAVE_GENEROS_AUDIO])):
                encontradas.append(audio[constantes.CLAVE_ID_AUDIO])

    if len(datosPodcasts) > 0:
        for audio in datosPodcasts:
            if (query.lower() in audio[constantes.CLAVE_NOMBRE_AUDIO].lower() or 
                query.lower() in audio[constantes.CLAVE_ARTISTA_AUDIO].lower() or
                query.lower() in audio[constantes.CLAVE_DESCRIPCION_AUDIO].lower() or 
                query.lower() in constantes.obtenerNombreGenero(audio[constantes.CLAVE_GENEROS_AUDIO])):
                encontradas.append(audio[constantes.CLAVE_ID_AUDIO])

    if len(datosArtistas) > 0:
        for artista in datosArtistas:
            if query.lower() in artista[constantes.CLAVE_ALIAS].lower():
                artistasEncontrados.append(artista[constantes.CLAVE_ID_USUARIO])

    if len(datosListas) > 0:
        for lista in datosListas:
            print (lista)
            if query.lower() in lista[constantes.CLAVE_NOMBRE_LISTA].lower() and lista[constantes.CLAVE_PRIVACIDAD_LISTA] == constantes.LISTA_PUBLICA:
                listasEncontradas.append(lista[constantes.CLAVE_ID_LISTA])
            
    return encontradas, artistasEncontrados, listasEncontradas


def getValoracionUsuario(r, idUsr, idAudio):
    valoracion =  r.get("valoraciones" + ":" + idUsr + ":" + idAudio)
    if(valoracion == None):
        valoracion = 0
    return valoracion

def setValoracionUsuario(r, idUsr, idAudio, val):
    r.set("valoraciones" + ":" + idUsr + ":" + idAudio, val)

# Funcion para obtener el num de veces que se ha escuchado una cancion
def obtenerVecesreproducidasCancion(r, id):
    return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de una cancion
def obtenerValMedia(r, id):
    val = r.hget("valoracionMedia:" + id, "media")

    if val == None:
        val = 0

    return val

# Funcion para obtener el genero de una cancion
def obtenerGeneroCancion(r, id):
    return int(r.hget(id, 'generos'))

# Funcion para obtener el nombre de una cancion
def obtenerNombreCancion(r, id):
    return r.hget(id, 'nombre')

# Funcion para obtener el artista de una cancion
def obtenerArtistaCancion(r, id):
    return r.hget(id, 'artista')

# Funcion para obtener la calidad de una cancion
def obtenerCalidad(r, id):
    return r.hget(id, 'calidad')

# Funcion para obtener el fichero de alta calidad de una cancion
def obtenerFicheroAltaCalidad(r, id):
    return r.hget(id+":ficheros", 'ficheroAltaCalidad')

# Funcion para obtener el fichero de baja calidad de una cancion
def obtenerFicheroBajaCalidad(r, id):
    return r.hget(id+":ficheros", 'ficheroBajaCalidad')
    
# Funcion para obtener la longitud de una cancion
def obtenerLongitudCancion(r, id):
    return r.hget(id, 'longitud')

# Funcion para obtener el numero de favoritos de una cancion
def obtenerNumFavoritosCancion(r, id):
    return r.hget(id, 'numFavoritos')

# Funcion para obtener el atributo esPodcast de un audio
def obtenerEsPodcast(r, id):
    return r.hget(id, 'esPodcast') == 'True'

def getImagenAudio(r, id):
    return r.hget(id, constantes.CLAVE_IMAGEN_AUDIO)

def setImagenAudio(r, id, imagen):
    return r.hset(id, constantes.CLAVE_IMAGEN_AUDIO, imagen)

def getImagenDefaultAudio(r):
    return r.get(constantes.CLAVE_DEFAULT_AUDIO_IMAGE)

#########################################################################################
#
#
# FUNCIONES PARA ALMACENAR/ACTUALIZAR PODCASTS
# Un podcast tiene los siguientes posibles atributos:
#   - id (clave para el hash)
#   - nombre
#   - artista
#   - calidad
#   - nVeces
#   - val
#   - desc
#  - ficheroAltaCalidad
#  - ficheroBajaCalidad
#  - longitud
#  - numFavoritos
#  - esPodcast
#
#
#########################################################################################

# Funcion para ver si existe un podcast
def existePodcast(r, id):
    if r.exists(id) == 0:
        return False
    else:
        return True

# Funcion para guardar un podcast en la base de datos
def guardarPodcast(r, podcastDic):
    print("Guardando cancion")
    id = podcastDic['id']
    ficheroAltaCalidad = podcastDic['ficheroAltaCalidad']
    ficheroBajaCalidad = podcastDic['ficheroBajaCalidad']

    # Ahora quito el id del diccionario para que no se guarde en el hash
    del podcastDic['id']
    del podcastDic['ficheroAltaCalidad']
    del podcastDic['ficheroBajaCalidad']

    r.hmset(id, podcastDic)
    r.hmset(id+":ficheros", {'ficheroAltaCalidad': ficheroAltaCalidad, 
                            'ficheroBajaCalidad': ficheroBajaCalidad})
    
    r.sadd(constantes.PREFIJO_LISTA_GLOBAL_PODCASTS, id)

    return 0


# Funcion para cambiar el nombre de un podcast
def cambiarNombrePodcast(r, id, nombre):
    r.hset(id, 'nombre', nombre)
    return 0

# Funcion para cambiar el artista de un podcast
def cambiarArtistaPodcast(r, id, artista):
    r.hset(id, 'artista', artista)
    return 0

# Funcion para cambiar la calidad de un podcast
def cambiarCalidadPodcast(r, id, calidad):
    r.hset(id, 'calidad', calidad)
    return 0

# Funcion para cambiar el num de veces que se ha escuchado un podcast
def cambiarVecesreproducidasPodcast(r, id, nVeces):
    r.hset(id, 'nVeces', nVeces)
    return 0

# Funcion para cambiar la valoracion de un podcast
def cambiarValPodcast(r, id, val):
    r.inc(id, 'nValoraciones')
    r.inc(id, 'val', int(val))

    return 0

# Funcion para cambiar la descripcion de un podcast
def cambiarDescPodcast(r, id, desc):
    r.hset(id, 'desc', desc)
    return 0

# Funcion para cambiar el fichero de alta calidad de un podcast
def cambiarFicheroAltaCalidadPodcast(r, id, ficheroAltaCalidad):
    r.hset(id+":ficheros", 'ficheroAltaCalidad', ficheroAltaCalidad)
    return 0

# Funcion para cambiar el fichero de baja calidad de un podcast
def cambiarFicheroBajaCalidadPodcast(r, id, ficheroBajaCalidad):
    r.hset(id+":ficheros", 'ficheroBajaCalidad', ficheroBajaCalidad)
    return 0

# Funcion para cambiar el genero de un podcast
def cambiarGeneroPodcast(r, id, genero):
    r.hset(id, 'generos', genero)
    return 0

# Funcion para cambiar la longitud de un podcast
def cambiarLongitudPodcast(r, id, longitud):
    r.hset(id, 'longitud', longitud)
    return 0

# Funcion para cambiar el numero de favoritos de un podcast
def cambiarNumFavoritosPodcast(r, id, numFavoritos):
    r.incrby(id, 'numFavoritos', numFavoritos)
    return 0

# Funcion para eliminar un podcast
def eliminarPodcast(r, id):
    r.delete(id)
    r.srem(constantes.PREFIJO_LISTA_GLOBAL_PODCASTS, id)
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER PODCASTS Y SUS ATRIBUTOS POR SEPARADO
#
#
#########################################################################################

# Funcion para obtener un podcast
def obtenerPodcast(r, id):
    datos_control = r.hgetall(id)
    datos_control['ficheroAltaCalidad'] = obtenerFicheroAltaCalidadPodcast(r, id)
    datos_control['ficheroBajaCalidad'] = obtenerFicheroBajaCalidadPodcast(r, id)

    return datos_control

# Devuelve los datos de control de un audio (sin los ficheros)
def obtenerDatosPodcast(r, id):
    return r.hgetall(id)

def obtenerTodosLosPodcasts(r):
    return r.smembers(constantes.PREFIJO_LISTA_GLOBAL_PODCASTS)


def obtenerDatosPodcasts(r, ids):
    datosPodcasts = []

    for id in ids:
        datos = obtenerDatosPodcast(r, id)
        datos[constantes.CLAVE_ID_AUDIO] = id
        datosPodcasts.append(datos)

    return datosPodcasts

# Funcion para obtener el nombre de un podcast
def obtenerNombrePodcast(r, id):
    return r.hget(id, 'nombre')

# Funcion para obtener el artista de un podcast
def obtenerArtistaPodcast(r, id):
    return r.hget(id, 'artista')

# Funcion para obtener la calidad de un podcast
def obtenerCalidadPodcast(r, id):
    return r.hget(id, 'calidad')

# Funcion para obtener el num de veces que se ha escuchado un podcast
def obtenerVecesreproducidasPodcast(r, id):
    return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de un podcast
def obtenerValPodcast(r, id):
    return int(r.hget(id, 'val')) / int(r.hget(id, 'nValoraciones'))

# Funcion para obtener la descripcion de un podcast
def obtenerDescPodcast(r, id):
    return r.hget(id, 'desc')

# Funcion para obtener el fichero de alta calidad de un podcast
def obtenerFicheroAltaCalidadPodcast(r, id):
    return r.hget(id+"ficheros", 'ficheroAltaCalidad')

# Funcion para obtener el fichero de baja calidad de un podcast
def obtenerFicheroBajaCalidadPodcast(r, id):
    return r.hget(id+"ficheros", 'ficheroBajaCalidad')
    
# Funcion para obtener el genero de un podcast
def obtenerGeneroPodcast(r, id):
    return r.hget(id, 'generos')
    
# Funcion para obtener la longitud de un podcast
def obtenerLongitudPodcast(r, id):
    return r.hget(id, 'longitud')

# Funcion para obtener el numero de favoritos de un podcast
def obtenerNumFavoritosPodcast(r, id):
    return r.hget(id, 'numFavoritos')

def setValoracionMedia(r, idAudio, val):
    valTotal = r.hget("valoracionMedia:" + idAudio, 'valTotal')
    if valTotal == None:
        valTotal = 0
    nValoraciones = r.hget("valoracionMedia:" + idAudio, 'nValoraciones')
    if nValoraciones == None:
        nValoraciones = 1
    r.hset("valoracionMedia:" + idAudio, 'valTotal', float(valTotal) + float(val))
    r.hset("valoracionMedia:" + idAudio, 'nValoraciones', int(nValoraciones) + 1)

    valoracion_media = float(r.hget("valoracionMedia:" + idAudio, 'valTotal')) / float(r.hget("valoracionMedia:" + idAudio, 'nValoraciones'))

    r.hset("valoracionMedia:" + idAudio, 'media', valoracion_media)
