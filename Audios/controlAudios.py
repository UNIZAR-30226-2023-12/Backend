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

# Función para almacenar una canción
def almacenarCancion(r, cancionDic):
    # Primero compruebo que la canción no existe
    if r.exists(cancionDic['id']):
        print('Error: La canción ' + cancionDic['id'] + ' ya existe')
        return -1
    else:
        # Almaceno la canción
        return daoAudio.guardarCancion(r, cancionDic)
    
# Función para cambiar los valores de una canción
# Si alguno de los valores no se quiere cambiar, se debe pasar como parámetro None (salvo el id)
def cambiarAtributosCancion(r, id, nombre, artista, calidad, nVeces, val, generos, ficheroAltaCalidad, ficheroBajaCalidad):
    # Compruebo que la canción existe
    if r.exists(id):
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
    else:
        print('Error: La canción ' + id + ' no existe')
        return -1
    
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