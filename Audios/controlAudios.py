##############################################################################################################
#
#
#   Este módulo contiene las funciones necesarias para el control de los audios
#
#
##############################################################################################################

import redis
from DAOS import daoAudio

##############################################################################################################
#
#
#   Funciones que controlan el modificado/añadido/eliminado de canciones
#
#
##############################################################################################################

# Función para obtener el id de la última canción añadida a la base
def IDUltimaCancion(r):
    return daoAudio.obtenerIDUltimaCancion(r)

# Función para incrementar el id de la última canción que se ha añadido
def incrementarIDUltimaCancion(r, id):
    daoAudio.incrementarIDCanciones(r, id)

# Función para almacenar una canción
def almacenarCancion(r, cancionDic):
    # Almaceno la canción
    return daoAudio.guardarCancion(r, cancionDic)
    
# Función para cambiar los valores de una canción
# Si alguno de los valores no se quiere cambiar, se debe pasar como parámetro None (salvo el id)
def cambiarAtributosCancion(r, id, nombre, artista, calidad, nVeces, val, generos, ficheroAltaCalidad, ficheroBajaCalidad):
    if nombre != None:
        daoAudio.cambiarNombreCancion(r, id, nombre)
    if artista != None:
        daoAudio.cambiarArtistaCancion(r, id, artista)
    if calidad != None:
        daoAudio.cambiarCalidadCancion(r, id, calidad)
    if nVeces != None:
        daoAudio.cambiarVecesreproducidasCancion(r, id, nVeces)
    if val != None:
        daoAudio.cambiarValCancion(r, id, val)
    if generos != None:
        daoAudio.cambiarGeneroCancion(r, id, generos)
    if ficheroAltaCalidad != None:
        daoAudio.cambiarFicheroAltaCalidad(r, id, ficheroAltaCalidad)
    if ficheroBajaCalidad != None:
        daoAudio.cambiarFicheroBajaCalidad(r, id, ficheroBajaCalidad)
    return 0
    
# Función para eliminar una canción
def borrarCancion(r, id):
    return daoAudio.borrarCancion(r, id)
    
##############################################################################################################
#
#
#   Funciones que controlan la obtención de datos de canciones
#
#
##############################################################################################################

# Función para obtener todos los datos de una canción
def obtenerTodosCancion(r, id):
    return daoAudio.obtenerCancion(r, id)

# Función para obtener el número de veces que se ha reproducido una canción
def obtenerVecesReproducidasCancion(r, id):
    return daoAudio.obtenerVecesreproducidasCancion(r, id)

# Función para obtener la valoración de una canción
def obtenerValoracionCancion(r, id):
    return daoAudio.obtenerValCancion(r, id)

# Función para obtener el genero de una canción
def obtenerGenCancion(r, id):
    return daoAudio.obtenerGeneroCancion(r, id)

# Función para obtener el nombre de una canción
def obtenerNomCancion(r, id):
    return daoAudio.obtenerNombreCancion(r, id)

# Función para obtener el artista de una canción
def obtenerArtCancion(r, id):
    return daoAudio.obtenerArtistaCancion(r, id)

# Función para obtener la calidad de una canción
def obtenerCalCancion(r, id):
    return daoAudio.obtenerCalidad(r, id)

# Función para obtener el fichero de alta calidad de una canción
def obtenerAltaCalidadCancion(r, id):
    return daoAudio.obtenerFicheroAltaCalidad(r, id)

# Función para obtener el fichero de baja calidad de una canción
def obtenerBajaCalidadCancion(r, id):
    return daoAudio.obtenerFicheroBajaCalidad(r, id)

##############################################################################################################
#
#
#   Funciones que controlan el modificado/añadido/eliminado de podcasts
#
#
##############################################################################################################

# Función para almacenar un podcast
def almacenarPodcast(r, podcastDic):
    # Almaceno el podcast
    return daoAudio.guardarPodcast(r, podcastDic)

# Función para cambiar los valores de un podcast
# Si alguno de los valores no se quiere cambiar, se debe pasar como parámetro None (salvo el id)
def cambiarAtributosPodcast(r, id, nombre, artista, calidad, nVeces, val, descripcion, ficheroAltaCalidad, ficheroBajaCalidad, episodios):
    if nombre != None:
        daoAudio.cambiarNombrePodcast(r, id, nombre)
    if artista != None:
        daoAudio.cambiarArtistaPodcast(r, id, artista)
    if calidad != None:
        daoAudio.cambiarCalidadPodcast(r, id, calidad)
    if nVeces != None:
        daoAudio.cambiarVecesreproducidasPodcast(r, id, nVeces)
    if val != None:
        daoAudio.cambiarValPodcast(r, id, val)
    if descripcion != None:
        daoAudio.cambiarDescPodcast(r, id, descripcion)
    if ficheroAltaCalidad != None:
        daoAudio.cambiarFicheroAltaCalidadPodcast(r, id, ficheroAltaCalidad)
    if ficheroBajaCalidad != None:
        daoAudio.cambiarFicheroBajaCalidadPodcast(r, id, ficheroBajaCalidad)
    return 0

# Función para eliminar un podcast
def borrarPodcast(r, id):
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
    return daoAudio.obtenerPodcast(r, id)

# Función para obtener el número de veces que se ha reproducido un podcast
def obtenerVecesReproducidasPodcast(r, id):
    return daoAudio.obtenerVecesreproducidasPodcast(r, id)

# Función para obtener la valoración de un podcast
def obtenerValoracionPodcast(r, id):
    return daoAudio.obtenerValPodcast(r, id)

# Función para obtener la descripción de un podcast
def obtenerDescPodcast(r, id):
    return daoAudio.obtenerDescPodcast(r, id)

# Función para obtener el nombre de un podcast
def obtenerNomPodcast(r, id):
    return daoAudio.obtenerNombrePodcast(r, id)

# Función para obtener el artista de un podcast
def obtenerArtPodcast(r, id):
    return daoAudio.obtenerArtistaPodcast(r, id)

# Función para obtener la calidad de un podcast
def obtenerCalPodcast(r, id):
    return daoAudio.obtenerCalidadPodcast(r, id)

# Función para obtener el fichero de alta calidad de un podcast
def obtenerAltaCalidadPodcast(r, id):
    return daoAudio.obtenerFicheroAltaCalidadPodcast(r, id)

# Función para obtener el fichero de baja calidad de un podcast
def obtenerBajaCalidadPodcast(r, id):
    return daoAudio.obtenerFicheroBajaCalidadPodcast(r, id)