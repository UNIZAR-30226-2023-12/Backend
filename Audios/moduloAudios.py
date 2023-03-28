##############################################################################################################
#
#
#   Este módulo es el "general" de audios a más alto nivel que usa las funciones de controlAudios y 
#   controlCalidadAudios para todo el control de audios.
#
#
##############################################################################################################

import controlAudios
import controlCalidadAudios

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
    id = controlAudios.IDUltimaCancion(r)

    # Incremento el id
    controlAudios.incrementarIDUltimaCancion(r, id+1)

    # Construyo el diccionario para almacenar los datos de la canción
    cancionDic = {'id': id, 'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'generos': generos, 'ficheroAltaCalidad': ficheroAltaCalidad, 'ficheroBajaCalidad': ficheroBajaCalidad}

    # Almaceno la canción
    controlAudios.almacenarCancion(r, cancionDic)

    return 0

# Función para eliminar una canción
def eliminarCancion(r, id):
    # Elimino la canción
    controlAudios.borrarCancion(r, id)

    return 0


    