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


# Funcion para guardar una cancion en la base de datos, modificada para trabajar con diccionarios
def guardarCancion(r, cancionDic):
    id = cancionDic['id']
    # Ahora quito el id del diccionario para que no se guarde en el hash
    del cancionDic['id']
    r.hmset(id, cancionDic)
    
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
    r.hset(id, 'val', val)
    return 0

# Funcion para cambiar el genero de una cancion
def cambiarGeneroCancion(r, id, genero):
    r.hset(id, 'generos', genero)
    return 0

# Funcion para cambiar el fichero de alta calidad de una cancion
def cambiarFicheroAltaCalidad(r, id, ficheroAltaCalidad):
    r.hset(id, 'ficheroAltaCalidad', ficheroAltaCalidad)
    return 0

# Funcion para cambiar el fichero de baja calidad de una cancion
def cambiarFicheroBajaCalidad(r, id, ficheroBajaCalidad):
    r.hset(id, 'ficheroBajaCalidad', ficheroBajaCalidad)     
    return 0

# Funcion para cambiar la longitud de una canción
def cambiarLongitudCancion(r, id, longitud):
    r.hset(id, 'longitud', longitud)    
    return 0

# Funcion para eliminar una cancion
def eliminarCancion(r, id):
    r.delete(id)     
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER CANCIONES Y SUS ATRIBUTOS POR SEPARADO
#
#
#########################################################################################

# Funcion para obtener una cancion
def obtenerCancion(r, id):
    return r.hgetall(id)

# Funcion para obtener el num de veces que se ha escuchado una cancion
def obtenerVecesreproducidasCancion(r, id):
    return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de una cancion
def obtenerValCancion(r, id):
    return r.hget(id, 'val')

# Funcion para obtener el genero de una cancion
def obtenerGeneroCancion(r, id):
    return r.hget(id, 'generos')

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
    return r.hget(id, 'ficheroAltaCalidad')

# Funcion para obtener el fichero de baja calidad de una cancion
def obtenerFicheroBajaCalidad(r, id):
    return r.hget(id, 'ficheroBajaCalidad')
    
# Funcion para obtener la longitud de una cancion
def obtenerLongitudCancion(r, id):
    return r.hget(id, 'longitud')

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
    id = podcastDic['id']
    # Ahora quito el id del diccionario para que no se guarde en el hash
    del podcastDic['id']

    r.hmset(id, podcastDic)
    
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
    r.hset(id, 'val', val)
    return 0

# Funcion para cambiar la descripcion de un podcast
def cambiarDescPodcast(r, id, desc):
    r.hset(id, 'desc', desc)
    return 0

# Funcion para cambiar el fichero de alta calidad de un podcast
def cambiarFicheroAltaCalidadPodcast(r, id, ficheroAltaCalidad):
    r.hset(id, 'ficheroAltaCalidad', ficheroAltaCalidad)
    return 0

# Funcion para cambiar el fichero de baja calidad de un podcast
def cambiarFicheroBajaCalidadPodcast(r, id, ficheroBajaCalidad):
    r.hset(id, 'ficheroBajaCalidad', ficheroBajaCalidad)
    return 0

# Funcion para cambiar el genero de un podcast
def cambiarGeneroPodcast(r, id, genero):
    r.hset(id, 'generos', genero)
    return 0

# Funcion para cambiar la longitud de un podcast
def cambiarLongitudPodcast(r, id, longitud):
    r.hset(id, 'longitud', longitud)
    return 0

# Funcion para eliminar un podcast
def eliminarPodcast(r, id):
    r.delete(id)
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
    return r.hgetall(id)

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
    return r.hget(id, 'val')

# Funcion para obtener la descripcion de un podcast
def obtenerDescPodcast(r, id):
    return r.hget(id, 'desc')

# Funcion para obtener el fichero de alta calidad de un podcast
def obtenerFicheroAltaCalidadPodcast(r, id):
    return r.hget(id, 'ficheroAltaCalidad')

# Funcion para obtener el fichero de baja calidad de un podcast
def obtenerFicheroBajaCalidadPodcast(r, id):
    return r.hget(id, 'ficheroBajaCalidad')
    
# Funcion para obtener el genero de un podcast
def obtenerGeneroPodcast(r, id):
    return r.hget(id, 'generos')
    
# Funcion para obtener la longitud de un podcast
def obtenerLongitudPodcast(r, id):
    return r.hget(id, 'longitud')
