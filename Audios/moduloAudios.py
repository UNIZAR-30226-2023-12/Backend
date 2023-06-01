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
from DAOS import daoAudio as dao
from Configuracion import constantesPrefijosClaves as constantes 
from Configuracion import constantesErroresHTTP as errores
from Usuarios import usuarios
##############################################################################################################
#
#
#   Funciones para canciones
#
#
##############################################################################################################

# Función que devuelve si existe una canción
def existeCancion(r, id):
    return controlAudios.existeCancion(r, id)

# Función para añadir una canción
# dic debe tener al menos los siguientes campos:
#   nombre
#   artista
#   calidad
#   generos
#   ficheroAltaCalidad
#   ficheroBajaCalidad
#   longitud
def anyadirCancion(r, dic):
    # Extraigo algunos datos del diccionario y otros los inicializo a 0,
    # ya que por ejemplo no tiene sentido que una canción tenga valoración o 
    # nVeces reproducidas cuando se está añadiendo
    nombre = dic['nombre']
    artista = dic['artista']
    calidad = dic['calidad']
    nVeces = 0
    val = 0
    nValoraciones = 0
    genero = dic['genero']
    longitud = dic['longitud']
    esPodcast = dic['esPodcast']

    # Obtiene la id del genero de las constantes
    idGenero = constantes.obtenerIDGenero(genero)

    if calidad == 'alta':
        ficheroAltaCalidad = dic['audio']
        ficheroBajaCalidad = controlCalidadAudios.convertirWavAMP3(ficheroAltaCalidad)
    elif calidad == 'baja':
        # Si no se dispone de fichero de alta calidad se inicia a -1
        ficheroAltaCalidad = '-1'
        ficheroBajaCalidad = dic['audio']
    else:
        print("Opción de calidad no válida")
        return errores.ERROR_CANCION_ELEMENTOS_VACIOS
    
    # Obtengo el id de la última canción que se ha añadido e incremento en 1
    id = controlAudios.IDUltimoAudio(r)

    id = 'idAudio:' + str(id)
    # Construyo el diccionario para almacenar los datos de la canción
    cancionDic = {'id': id, 'nombre': nombre, 'artista': artista, 
                  'calidad': calidad, 'nVeces': nVeces, 'val': val, 
                  'generos': idGenero, 'ficheroAltaCalidad': ficheroAltaCalidad, 
                  'ficheroBajaCalidad': ficheroBajaCalidad, 'longitud': longitud, 
                  'numFavoritos': 0, 'esPodcast': esPodcast, 'nValoraciones': nValoraciones}

    #print("Cancion a almacenar: " + str(cancionDic))
    # Almaceno la canción
    controlAudios.almacenarCancion(r, cancionDic)

    # Añado la canción a la lista de canciones del artista
    usuarios.anyadirCancionArtista(r, artista, id)

    return id

# Función para eliminar una canción
def eliminarCancion(r, id):
    # Elimino la canción
    return controlAudios.borrarCancion(r, id)

# Función para devolver el audio de una canción ya sea el de alta calidad o el de baja calidad
def obtenerFicheroCancion(r, id, calidad):
    listaFicheros = []
    cal = controlAudios.obtenerCalCancion(r, id)
    if cal == 'alta' and calidad == 'alta':
        listaFicheros = controlAudios.obtenerAltaCalidadCancion(r, id)
    else:
        listaFicheros = controlAudios.obtenerBajaCalidadCancion(r, id)
    
    return listaFicheros

# Función para cambiar los atributos de una canción
# Si alguno de los valores disponibles no se quiere cambiar, se debe pasar como None en el dic (salvo el id)
def modificarCancion(r, id, dic):
    # Compruebo que el dic tenga todo lo necesario
    if 'nombre' not in dic or 'artista' not in dic or 'calidad' not in dic or 'generos' not in dic or 'ficheroAltaCalidad' not in dic or 'ficheroBajaCalidad' not in dic or 'nVeces' not in dic or 'val' not in dic or 'longitud' not in dic:
        print("Diccionario no válido")
        return -1
    else:
        return controlAudios.cambiarAtributosCancion(r, id, dic['nombre'], dic['artista'], dic['calidad'], dic['nVeces'], dic['val'], dic['generos'], dic['ficheroAltaCalidad'], dic['ficheroBajaCalidad'], dic['longitud'])
    
# Función para obtener el diccionario de una canción
def obtenerDiccionarioCancion(r, id):
    controlAudios.addReproduccion(r, id)
    return controlAudios.obtenerTodosCancion(r, id)


def obtenerTodasLasCanciones(r):
    audios = dao.obtenerTodasLasCanciones(r)
    return audios

def obtenerTodosLosPodcasts(r):
    return dao.obtenerTodosLosPodcasts(r)


# Función de búsqueda de canciones
def buscarCanciones(r, query, n):
    respuesta, artistas = dao.buscarAudios(r, query)

    return respuesta[0:n]

def getValoracion(r, idUsr, idAudio):
    return dao.getValoracionUsuario(r, idUsr, idAudio)

def setValoracion(r, idUsr, idAudio, val):
    dao.setValoracionMedia(r, idAudio, val)
    return dao.setValoracionUsuario(r, idUsr, idAudio, val)

def buscarGeneral(r, query, n):
    respuesta, artistas, listas = dao.buscarAudios(r, query)

    return respuesta[0:n], artistas[0:n], listas[0:n]

def obtenerValMedia(r, idAudio):
    return dao.obtenerValMedia(r, idAudio)



##############################################################################################################
#
#
#   Funciones para podcasts
#
#
##############################################################################################################

# Función que devuelve si existe un podcast
def existePodcast(r, id):
    return controlAudios.existePodcast(r, id)

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
#   longitud
#   generos
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
    longitud = dic['longitud']
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
    
    # Obtengo el id del último podcast que se ha añadido
    id = controlAudios.IDUltimoAudio(r)

    id = 'idAudio:' + str(id)

    # Construyo el diccionario para almacenar los datos del podcast
    podcastDic = {'id': id, 'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'desc': desc, 'ficheroAltaCalidad': ficheroAltaCalidad, 'ficheroBajaCalidad': ficheroBajaCalidad, 'longitud': longitud, 'generos': generos}

    # Almaceno el podcast
    controlAudios.almacenarPodcast(r, podcastDic)

    return 0

def cambiarValAudio(r, id, val):
    if controlAudios.obtenerEsPodcast(r, id):
        return dao.cambiarValCancion(r, id, val)
    else:
        return dao.cambiarValPodcast(r, id, val)
    
def obtenerValAudio(r, id):
    if controlAudios.obtenerEsPodcast(r, id):
        return dao.obtenerValCancion(r, id)
    else:
        return dao.obtenerValPodcast(r, id)
    


def setLastSecondHeared(r, idUsuario, idAudio, second):
    return dao.setLastSecondHeared(r, idUsuario, idAudio, second)

def getReproducciones(r, id):
    return controlAudios.getReproducciones(r, id)

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
    if 'nombre' not in dic or 'artista' not in dic or 'calidad' not in dic or 'desc' not in dic or 'ficheroAltaCalidad' not in dic or 'ficheroBajaCalidad' not in dic or 'nVeces' not in dic or 'val' not in dic or 'longitud' not in dic or 'generos' not in dic:
        print("Diccionario no válido")
        return -1
    else:
        return controlAudios.cambiarAtributosPodcast(r, id, dic['nombre'], dic['artista'], dic['calidad'], dic['nVeces'], dic['val'], dic['desc'], dic['ficheroAltaCalidad'], dic['ficheroBajaCalidad'], dic['longitud'], dic['generos'])
    
# Función para obtener el diccionario de un podcast (todos los atributos del mismo)
def obtenerDiccionarioPodcast(r, id):
    return controlAudios.obtenerTodosPodcast(r, id)

def getImagenAudio(r, id):
    return controlAudios.getImagenAudio(r, id)

def setImagenAudio(r, id, imagen):
    return controlAudios.setImagenAudio(r, id, imagen)