##############################################################################################################
#
#
#   Este módulo es el "general" de audios a más alto nivel que usa las funciones de controlAudios y 
#   controlCalidadAudios para todo el control de audios.
#
#
##############################################################################################################

from Audios import controlAudios
from Audios import controlCalidadAudios

##############################################################################################################
#
#
#   Funciones para canciones
#
#
##############################################################################################################

# Función para añadir una canción
# dic debe tener al menos los siguientes campos:
#   nombre
#   artista
#   calidad
#   generos
#   ficheroAltaCalidad
#   ficheroBajaCalidad
def anyadirCancion(r, dic):
    # Extraigo algunos datos del diccionario y otros los inicializo a 0,
    # ya que por ejemplo no tiene sentido que una canción tenga valoración o 
    # nVeces reproducidas cuando se está añadiendo
    nombre = dic['nombre']
    artista = dic['artista']
    calidad = dic['calidad']
    nVeces = 0
    val = 0
    generos = dic['generos']

    if calidad == 'alta':
        ficheroAltaCalidad = dic['ficheroAltaCalidad']
        ficheroBajaCalidad = controlCalidadAudios.convertirWavAMP3(ficheroAltaCalidad)
    elif calidad == 'baja':
        # Si no se dispone de fichero de alta calidad se inicia a -1
        ficheroAltaCalidad = '-1'
        ficheroBajaCalidad = dic['ficheroBajaCalidad']
    else:
        print("Opción de calidad no válida")
        return -1
    
    # Obtengo el id de la última canción que se ha añadido
    id = controlAudios.IDUltimoAudio(r)

    # Incremento el id
    controlAudios.incrementarIDUltimoAudio(r, id+1)

    id = 'idAudio:' + str(id)
    # Construyo el diccionario para almacenar los datos de la canción
    cancionDic = {'id': id, 'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'generos': generos, 'ficheroAltaCalidad': ficheroAltaCalidad, 'ficheroBajaCalidad': ficheroBajaCalidad}

    # Almaceno la canción
    controlAudios.almacenarCancion(r, cancionDic)

    return 0

# Función para eliminar una canción
def eliminarCancion(r, id):
    # Elimino la canción
    return controlAudios.borrarCancion(r, id)

# Función para devolver el audio de una canción ya sea el de alta calidad o el de baja calidad
def obtenerFicheroCancion(r, id, calidad):
    # Obtengo el diccionario de la canción
    cal = controlAudios.obtenerCalCancion(r, id)

    # Obtengo el fichero de la canción
    if calidad == 'alta' and cal == 'alta':
        fichero = controlAudios.obtenerAltaCalidadCancion(r, id)
    else:
        fichero = controlAudios.obtenerBajaCalidadCancion(r, id)

    return fichero

# Función para cambiar los atributos de una canción
# Si alguno de los valores disponibles no se quiere cambiar, se debe pasar como None en el dic (salvo el id)
def modificarCancion(r, id, dic):
    # Compruebo que el dic tenga todo lo necesario
    if 'nombre' not in dic or 'artista' not in dic or 'calidad' not in dic or 'generos' not in dic or 'ficheroAltaCalidad' not in dic or 'ficheroBajaCalidad' not in dic or nVeces not in dic or val not in dic:
        print("Diccionario no válido")
        return -1
    else:
        return controlAudios.cambiarAtributosCancion(r, id, dic['nombre'], dic['artista'], dic['calidad'], dic['nVeces'], dic['val'], dic['generos'], dic['ficheroAltaCalidad'], dic['ficheroBajaCalidad'])
    
# Función para obtener el diccionario de una canción
def obtenerDiccionarioCancion(r, id):
    return controlAudios.obtenerTodosCancion(r, id)

##############################################################################################################
#
#
#   Funciones para podcasts
#
#
##############################################################################################################

# Función para añadir un podcast
# dic debe tener al menos los siguientes campos:
#   nombre
#   artista
#   calidad
#   desc
#   val
#   nVeces
#   ficheroAltaCalidad
#   ficheroBajaCalidad
def anyadirPodcast(r, dic):
    # Extraigo algunos datos del diccionario y otros los inicializo a 0,
    # ya que por ejemplo no tiene sentido que una canción tenga valoración o 
    # nVeces reproducidas cuando se está añadiendo
    nombre = dic['nombre']
    artista = dic['artista']
    calidad = dic['calidad']
    nVeces = 0
    val = 0
    desc = dic['desc']

    if calidad == 'alta':
        ficheroAltaCalidad = dic['ficheroAltaCalidad']
        ficheroBajaCalidad = controlCalidadAudios.convertirWavAMP3(ficheroAltaCalidad)
    elif calidad == 'baja':
        # Si no se dispone de fichero de alta calidad se inicia a -1
        ficheroAltaCalidad = '-1'
        ficheroBajaCalidad = dic['ficheroBajaCalidad']
    else:
        print("Opción de calidad no válida")
        return -1
    
    # Obtengo el id del último podcast que se ha añadido
    id = controlAudios.IDUltimoPodcast(r)

    # Incremento el id
    controlAudios.incrementarIDUltimoPodcast(r, id+1)

    id = 'idAudio:' + str(id)

    # Construyo el diccionario para almacenar los datos del podcast
    podcastDic = {'id': id, 'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'desc': desc, 'ficheroAltaCalidad': ficheroAltaCalidad, 'ficheroBajaCalidad': ficheroBajaCalidad}

    # Almaceno el podcast
    controlAudios.almacenarPodcast(r, podcastDic)

    return 0

# Función para eliminar un podcast
def eliminarPodcast(r, id):
    # Elimino el podcast
    return controlAudios.borrarPodcast(r, id)

# Función para devolver el audio de un podcast ya sea el de alta calidad o el de baja calidad
def obtenerFicheroPodcast(r, id, calidad):
    # Obtengo el diccionario del podcast
    cal = controlAudios.obtenerCalPodcast(r, id)

    # Si el podcast está almacenado en alta calidad y el usuario quiere obtenerlo en alta calidad se le 
    # devuelve el fichero de alta calidad sino el de baja calidad
    # Obtengo el fichero del podcast
    if calidad == 'alta' and cal == 'alta':
        fichero = controlAudios.obtenerAltaCalidadPodcast(r, id)
    else:
        fichero = controlAudios.obtenerBajaCalidadPodcast(r, id)

    return fichero

# Función para cambiar los atributos de un podcast
# Si alguno de los valores disponibles no se quiere cambiar, se debe pasar como None en el dic (salvo el id)
def modificarPodcast(r, id, dic):
    # Compruebo que el dic tenga todo lo necesario
    if 'nombre' not in dic or 'artista' not in dic or 'calidad' not in dic or 'desc' not in dic or 'ficheroAltaCalidad' not in dic or 'ficheroBajaCalidad' not in dic or 'nVeces' not in dic or 'val' not in dic:
        print("Diccionario no válido")
        return -1
    else:
        return controlAudios.cambiarAtributosPodcast(r, id, dic['nombre'], dic['artista'], dic['calidad'], dic['nVeces'], dic['val'], dic['desc'], dic['ficheroAltaCalidad'], dic['ficheroBajaCalidad'])
    
# Función para obtener el diccionario de un podcast (todos los atributos del mismo)
def obtenerDiccionarioPodcast(r, id):
    return controlAudios.obtenerTodosPodcast(r, id)