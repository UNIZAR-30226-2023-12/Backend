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

# Función para incrementar el id artificial
def incrementarIDAudio(r, id):
    r.set('idUltimoAudio', id)

# Funcion para guardar una cancion en la base de datos, modificada para trabajar con diccionarios
def guardarCancion(r, cancionDic):
    # Antes de guardar compruebo si el diccionario contiene todas las claves necesarias
    if 'id' not in cancionDic or 'nombre' not in cancionDic or 'artista' not in cancionDic or 'calidad' not in cancionDic or 'nVeces' not in cancionDic or 'val' not in cancionDic or 'generos' not in cancionDic or 'ficheroAltaCalidad' not in cancionDic or 'ficheroBajaCalidad' not in cancionDic:
        print('ERROR: No se ha podido guardar la cancion, falta el algunas de las claves necesarias o tienen el nombre incorrecto')
        return -1
    else:
        if id == '':
            print('ERROR: No se ha podido guardar la cancion, el id no puede estar vacio')
            return -1
        else:
            id = cancionDic['id']
            # Ahora quito el id del diccionario para que no se guarde en el hash
            del cancionDic['id']
            r.hmset(id, cancionDic)
    
    return 0

# Funcion para cambiar el nombre de una cancion
def cambiarNombreCancion(r, id, nombre):
    if nombre == '':
        print('ERROR: No se ha podido cambiar el nombre de la cancion, el nombre no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el nombre de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'nombre', nombre)

    return 0

# Funcion para cambiar el artista de una cancion
def cambiarArtistaCancion(r, id, artista):
    if artista == '':
        print('ERROR: No se ha podido cambiar el artista de la cancion, el artista no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el artista de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'artista', artista)

    return 0

# Funcion para cambiar la calidad de una cancion
def cambiarCalidadCancion(r, id, calidad):
    if calidad == '':
        print('ERROR: No se ha podido cambiar la calidad de la cancion, la calidad no puede estar vacia')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar la calidad de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'calidad', calidad)
    
    return 0

# Funcion para cambiar el num de veces que se ha escuchado una cancion
def cambiarVecesreproducidasCancion(r, id, nVeces):
    if nVeces == '':
        print('ERROR: No se ha podido cambiar el num de veces que se ha escuchado la cancion, el num no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el num de veces que se ha escuchado la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'nVeces', nVeces)
    
    return 0

# Funcion para cambiar la valoracion de una cancion
def cambiarValCancion(r, id, val):
    if val == '':
        print('ERROR: No se ha podido cambiar la valoracion de la cancion, la valoracion no puede estar vacia')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar la valoracion de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'val', val)

    return 0

# Funcion para cambiar el genero de una cancion
def cambiarGeneroCancion(r, id, genero):
    if genero == '':
        print('ERROR: No se ha podido cambiar el genero de la cancion, el genero no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el genero de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'generos', genero)

    return 0

# Funcion para cambiar el fichero de alta calidad de una cancion
def cambiarFicheroAltaCalidad(r, id, ficheroAltaCalidad):
    if ficheroAltaCalidad == '':
        print('ERROR: No se ha podido cambiar el fichero de alta calidad de la cancion, el fichero no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el fichero de alta calidad de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'ficheroAltaCalidad', ficheroAltaCalidad)

    return 0

# Funcion para cambiar el fichero de baja calidad de una cancion
def cambiarFicheroBajaCalidad(r, id, ficheroBajaCalidad):
    if ficheroBajaCalidad == '':
        print('ERROR: No se ha podido cambiar el fichero de baja calidad de la cancion, el fichero no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el fichero de baja calidad de la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.hset(id, 'ficheroBajaCalidad', ficheroBajaCalidad)
        
    return 0

# Funcion para eliminar una cancion
def eliminarCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido eliminar la cancion, el id no puede estar vacio')
        return -1
    else:
        # Compruebo si existe una cancion con ese id
        if r.exists(id) == 0:
            print('ERROR: No se ha podido eliminar la cancion, no existe ninguna cancion con ese id')
            return -1
        else:
            r.delete(id)
        
    return 0

#########################################################################################
#
#
# FUNCIONES PARA OBTENER CANCIONES Y SUS ATRIBUTOS POR SEPARADO
#
#
#########################################################################################

# Funcion para obtener el id de la última canción que se ha añadido
def obtenerIDUltimoAudio(r):
    return r.get('idUltimoAudio')
# Funcion para obtener una cancion
def obtenerCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hgetall(id)

# Funcion para obtener el num de veces que se ha escuchado una cancion
def obtenerVecesreproducidasCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el num de veces que se ha escuchado la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de una cancion
def obtenerValCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener la valoracion de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'val')

# Funcion para obtener el genero de una cancion
def obtenerGeneroCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el genero de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'generos')

# Funcion para obtener el nombre de una cancion
def obtenerNombreCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el nombre de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'nombre')

# Funcion para obtener el artista de una cancion
def obtenerArtistaCancion(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el artista de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'artista')

# Funcion para obtener la calidad de una cancion
def obtenerCalidad(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener la calidad de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'calidad')

# Funcion para obtener el fichero de alta calidad de una cancion
def obtenerFicheroAltaCalidad(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el fichero de alta calidad de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'ficheroAltaCalidad')

# Funcion para obtener el fichero de baja calidad de una cancion
def obtenerFicheroBajaCalidad(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el fichero de baja calidad de la cancion, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'ficheroBajaCalidad')

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

# Funcion para guardar un podcast en la base de datos
def guardarPodcast(r, podcastDic):
    # Compruebo que el diccionario tenga todos los atributos necesarios
    if 'id' not in podcastDic or 'nombre' not in podcastDic or 'artista' not in podcastDic or 'calidad' not in podcastDic or 'nVeces' not in podcastDic or 'val' not in podcastDic or 'desc' not in podcastDic or 'ficheroAltaCalidad' not in podcastDic or 'ficheroBajaCalidad' not in podcastDic:
        print('ERROR: No se ha podido guardar el podcast, el diccionario no tiene todos los atributos necesarios')
        return -1
    else:
        # Compruebo que el id no este vacio
        if podcastDic['id'] == '':
            print('ERROR: No se ha podido guardar el podcast, el id no puede estar vacio')
            return -1
        else:
            id = podcastDic['id']
            # Ahora quito el id del diccionario para que no se guarde en el hash
            del podcastDic['id']
        
            r.hmset(id, podcastDic)
    
    return 0

# Funcion para cambiar el nombre de un podcast
def cambiarNombrePodcast(r, id, nombre):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar el nombre del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el nombre del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'nombre', nombre)
    return 0

# Funcion para cambiar el artista de un podcast
def cambiarArtistaPodcast(r, id, artista):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar el artista del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el artista del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'artista', artista)
    return 0

# Funcion para cambiar la calidad de un podcast
def cambiarCalidadPodcast(r, id, calidad):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar la calidad del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar la calidad del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'calidad', calidad)
    return 0

# Funcion para cambiar el num de veces que se ha escuchado un podcast
def cambiarVecesreproducidasPodcast(r, id, nVeces):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar el num de veces que se ha escuchado el podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el num de veces que se ha escuchado el podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'nVeces', nVeces)
    return 0

# Funcion para cambiar la valoracion de un podcast
def cambiarValPodcast(r, id, val):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar la valoracion del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar la valoracion del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'val', val)
    return 0

# Funcion para cambiar la descripcion de un podcast
def cambiarDescPodcast(r, id, desc):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar la descripcion del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar la descripcion del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'desc', desc)
    return 0

# Funcion para cambiar el fichero de alta calidad de un podcast
def cambiarFicheroAltaCalidadPodcast(r, id, ficheroAltaCalidad):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar el fichero de alta calidad del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el fichero de alta calidad del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'ficheroAltaCalidad', ficheroAltaCalidad)
    return 0

# Funcion para cambiar el fichero de baja calidad de un podcast
def cambiarFicheroBajaCalidadPodcast(r, id, ficheroBajaCalidad):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido cambiar el fichero de baja calidad del podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido cambiar el fichero de baja calidad del podcast, el podcast no existe')
            return -1
        else:
            r.hset(id, 'ficheroBajaCalidad', ficheroBajaCalidad)
    return 0

# Funcion para eliminar un podcast
def eliminarPodcast(r, id):
    # Compruebo que exista el podcast y no sea id vacio
    if id == '':
        print('ERROR: No se ha podido eliminar el podcast, el id no puede estar vacio')
        return -1
    else:
        if r.exists(id) == 0:
            print('ERROR: No se ha podido eliminar el podcast, el podcast no existe')
            return -1
        else:
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
    if id == '':
        print('ERROR: No se ha podido obtener el podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hgetall(id)

# Funcion para obtener el nombre de un podcast
def obtenerNombrePodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el nombre del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'nombre')

# Funcion para obtener el artista de un podcast
def obtenerArtistaPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el artista del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'artista')

# Funcion para obtener la calidad de un podcast
def obtenerCalidadPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener la calidad del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'calidad')

# Funcion para obtener el num de veces que se ha escuchado un podcast
def obtenerVecesreproducidasPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el num de veces que se ha escuchado el podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de un podcast
def obtenerValPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener la valoracion del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'val')

# Funcion para obtener la descripcion de un podcast
def obtenerDescPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener la descripcion del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'desc')

# Funcion para obtener el fichero de alta calidad de un podcast
def obtenerFicheroAltaCalidadPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el fichero de alta calidad del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'ficheroAltaCalidad')

# Funcion para obtener el fichero de baja calidad de un podcast
def obtenerFicheroBajaCalidadPodcast(r, id):
    if id == '':
        print('ERROR: No se ha podido obtener el fichero de baja calidad del podcast, el id no puede estar vacio')
        return -1
    else:
        return r.hget(id, 'ficheroBajaCalidad')
