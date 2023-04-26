##############################################################################################################
#
#
#   Este módulo contiene las funciones necesarias para el control de los audios
#
#
##############################################################################################################

import redis
from DAOS import daoAudio
from Configuracion import constantesErroresHTTP



##############################################################################################################
#
#
#   Funciones que controlan el modificado/añadido/eliminado de canciones
#
#
##############################################################################################################

# Función que devuelve si existe una canción
def existeCancion(r, id):
    return daoAudio.existeCancion(r, id)

# Función para obtener el id del último audio que se ha añadido
def IDUltimoAudio(r):
    return daoAudio.incrementarIDUltimoAudio(r)

# Función para almacenar una canción
def almacenarCancion(r, cancionDic):
    # Antes de guardar compruebo si el diccionario contiene todas las claves necesarias
    if 'id' not in cancionDic or 'nombre' not in cancionDic or 'artista' not in cancionDic or 'calidad' not in cancionDic or 'nVeces' not in cancionDic or 'val' not in cancionDic or 'generos' not in cancionDic or 'ficheroAltaCalidad' not in cancionDic or 'ficheroBajaCalidad' not in cancionDic or 'longitud' not in cancionDic or 'numFavoritos' not in cancionDic or 'esPodcast' not in cancionDic:
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_FALTANTES
    else:
        if cancionDic['id'] == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        
        return daoAudio.guardarCancion(r, cancionDic)
    
# Función para cambiar los valores de una canción
# Si alguno de los valores no se quiere cambiar, se debe pasar como parámetro None (salvo el id)
def cambiarAtributosCancion(r, id, nombre, artista, calidad, nVeces, val, generos, ficheroAltaCalidad, ficheroBajaCalidad, longitud, numFavoritos, esPodcast):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA

    if nombre != None:
        if nombre == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarNombreCancion(r, id, nombre)
    if artista != None:
        if artista == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarArtistaCancion(r, id, artista)
    if calidad != None:
        if calidad == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarCalidadCancion(r, id, calidad)
    if nVeces != None:
        if nVeces == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarVecesreproducidasCancion(r, id, nVeces)
    if val != None:
        if val == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarValCancion(r, id, val)
    if generos != None:
        if generos == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarGeneroCancion(r, id, generos)
    if ficheroAltaCalidad != None:
        if ficheroAltaCalidad == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarFicheroAltaCalidad(r, id, ficheroAltaCalidad)
    if ficheroBajaCalidad != None:
        if ficheroBajaCalidad == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarFicheroBajaCalidad(r, id, ficheroBajaCalidad)
    if longitud != None:
        if longitud == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarLongitudCancion(r, id, longitud)
    if numFavoritos != None:
        if numFavoritos == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarNumFavoritosCancion(r, id, numFavoritos)
    if esPodcast != None:
        if esPodcast == '':
            return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
        daoAudio.cambiarEsPodcastCancion(r, id, esPodcast)
    return 0
    
# Función para eliminar una canción
def borrarCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.eliminarCancion(r, id)
    
##############################################################################################################
#
#
#   Funciones que controlan la obtención de datos de canciones
#
#
##############################################################################################################

# Función para obtener todos los datos de una canción
def obtenerTodosCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerCancion(r, id)

# Función para obtener el número de veces que se ha reproducido una canción
def obtenerVecesReproducidasCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerVecesreproducidasCancion(r, id)

# Función para obtener la valoración de una canción
def obtenerValoracionCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerValCancion(r, id)

# Función para obtener el genero de una canción
def obtenerGenCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerGeneroCancion(r, id)

# Función para obtener el nombre de una canción
def obtenerNomCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerNombreCancion(r, id)

# Función para obtener el artista de una canción
def obtenerArtCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerArtistaCancion(r, id)

# Función para obtener la calidad de una canción
def obtenerCalCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerCalidad(r, id)

# Función para obtener el fichero de alta calidad de una canción
def obtenerAltaCalidadCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerFicheroAltaCalidad(r, id)

# Función para obtener el fichero de baja calidad de una canción
def obtenerBajaCalidadCancion(r, id):
    # Compruebo que la canción existe y que el id no sea vacío
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    
    return daoAudio.obtenerFicheroBajaCalidad(r, id)

# Función para obtener la longitud de una canción
def obtenerLongitudCancion(r, id):
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA

    return daoAudio.obtenerLongitudCancion(r, id)

# Función para obtener numFavoritos de una canción
def obtenerNumFavoritosCancion(r, id):
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA

    return daoAudio.obtenerNumFavoritosCancion(r, id)

# Función para obtener si un audio esPodcast
def obtenerEsPodcast(r, id):
    if id == '':
        return constantesErroresHTTP.ERROR_CANCION_ELEMENTOS_VACIOS
    if daoAudio.existeCancion(r, id) == False:
        return constantesErroresHTTP.ERROR_CANCION_NO_ENCONTRADA
    elif daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO

    return daoAudio.obtenerEsPodcast(r, id)

# Función para obtener las canciones 


##############################################################################################################
#
#
#   Funciones que controlan el modificado/añadido/eliminado de podcasts
#
#
##############################################################################################################

# Función que devuelve si existe un podcast
def existePodcast(r, id):
    return daoAudio.existePodcast(r, id)

# Función para almacenar un podcast
def almacenarPodcast(r, podcastDic):
    # Compruebo que el diccionario tenga los atributos necesarios
    if 'id' not in podcastDic or 'nombre' not in podcastDic or 'artista' not in podcastDic or 'calidad' not in podcastDic or 'nVeces' not in podcastDic or 'val' not in podcastDic or 'desc' not in podcastDic or 'ficheroAltaCalidad' not in podcastDic or 'ficheroBajaCalidad' not in podcastDic or 'generos' not in podcastDic or 'longitud' not in podcastDic or 'esPodcast' not in podcastDic or 'numFavoritos' not in podcastDic:
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_FALTANTES
    else:
        # Compruebo que el id no esté vacío
        if podcastDic['id'] == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        # Almaceno el podcast
        return daoAudio.guardarPodcast(r, podcastDic)

# Función para cambiar los valores de un podcast
# Si alguno de los valores no se quiere cambiar, se debe pasar como parámetro None (salvo el id)
def cambiarAtributosPodcast(r, id, nombre, artista, calidad, nVeces, val, descripcion, ficheroAltaCalidad, ficheroBajaCalidad, longitud, generos, esPodcast, numFavoritos):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    if nombre != None:
        if nombre == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarNombrePodcast(r, id, nombre)
    if artista != None:
        if artista == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarArtistaPodcast(r, id, artista)
    if calidad != None:
        if calidad == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarCalidadPodcast(r, id, calidad)
    if nVeces != None:
        if nVeces == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarVecesreproducidasPodcast(r, id, nVeces)
    if val != None:
        if val == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarValPodcast(r, id, val)
    if descripcion != None:
        if descripcion == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarDescPodcast(r, id, descripcion)
    if ficheroAltaCalidad != None:
        if ficheroAltaCalidad == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarFicheroAltaCalidadPodcast(r, id, ficheroAltaCalidad)
    if ficheroBajaCalidad != None:
        if ficheroBajaCalidad == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarFicheroBajaCalidadPodcast(r, id, ficheroBajaCalidad)
    if longitud != None:
        if longitud == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarLongitudPodcast(r, id, longitud)
    if generos != None:
        if generos == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarGeneroPodcast(r, id, generos)
    if esPodcast != None:
        if esPodcast == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarEsPodcastPodcast(r, id, esPodcast)
    if numFavoritos != None:
        if numFavoritos == '':
            return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
        daoAudio.cambiarNumFavoritosPodcast(r, id, numFavoritos)
    return 0

# Función para eliminar un podcast
def borrarPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.borrarPodcast(r, id)

##############################################################################################################
#
#
#   Funciones que controlan la obtención de datos de podcasts
#
#
##############################################################################################################

# Función para obtener todos los datos de un podcast
def obtenerTodosPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerPodcast(r, id)

# Función para obtener el número de veces que se ha reproducido un podcast
def obtenerVecesReproducidasPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerVecesreproducidasPodcast(r, id)

# Función para obtener la valoración de un podcast
def obtenerValoracionPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerValPodcast(r, id)

# Función para obtener la descripción de un podcast
def obtenerDescPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerDescPodcast(r, id)

# Función para obtener el nombre de un podcast
def obtenerNomPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerNombrePodcast(r, id)

# Función para obtener el artista de un podcast
def obtenerArtPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerArtistaPodcast(r, id)

# Función para obtener la calidad de un podcast
def obtenerCalPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerCalidadPodcast(r, id)

# Función para obtener el fichero de alta calidad de un podcast
def obtenerAltaCalidadPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerFicheroAltaCalidadPodcast(r, id)

# Función para obtener el fichero de baja calidad de un podcast
def obtenerBajaCalidadPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerFicheroBajaCalidadPodcast(r, id)

# Función para obtener la longitud de un podcast
def obtenerLongitudPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerLongitudPodcast(r, id)

# Función para obtener los generos de un podcast
def obtenerGenerosPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerGenerosPodcast(r, id)

# Función para obtener el número de favoritos de un podcast
def obtenerFavoritosPodcast(r, id):
    # Compruebo que el id no esté vacío y que el podcast exista
    if id == '':
        return constantesErroresHTTP.ERROR_PODCAST_ELEMENTOS_VACIOS
    if daoAudio.existePodcast(r, id) == False:
        return constantesErroresHTTP.ERROR_PODCAST_NO_ENCONTRADO
    return daoAudio.obtenerNumFavoritosPodcast(r, id)