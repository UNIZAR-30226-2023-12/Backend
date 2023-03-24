##############################################################################################################
#
#
#   Este módulo contiene las funciones necesarias para gestionar las conversiones necesarias de wav a mp3
#
#
##############################################################################################################

import base64
from pydub import AudioSegment
import os

# Recibe un string con el binario del audio wav codificado en UTF-8 y lo convierte al binario correspondiente en UTF-8 en mp3
def convertirWavAMP3(cadena):
    # Primero decodifico la cadena para obtener los datos
    datos = base64.b64decode(cadena)

    # Creo un fichero temporal con los datos
    with open('temporal.wav', 'wb') as f:
        f.write(datos)

    # Convierto el fichero temporal a mp3
    sound = AudioSegment.from_wav('temporal.wav')
    sound.export('temporal.mp3', format='mp3')

    # Leo el archivo binario del mp3 para obtener la cadena
    with open('temporal.mp3', 'rb') as g:
        mp3_data = g.read()

    # Codifico la cadena en base64
    mp3_string = base64.b64encode(mp3_data).decode('utf-8')

    # Elimino los ficheros temporales
    os.remove('temporal.wav')
    os.remove('temporal.mp3')

    return mp3_string