import redis
import Configuracion.constantesPrefijosClaves as constantes

# Daos para las estadisitcas de segundos reproducidos de los audios
def setSegundosReproduciodosAudio(r, idAudio, segundos):
    r.set(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO + ":" + idAudio, segundos)

def getSegundosReproduciodosAudio(r, idAudio):
    return r.get(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO + ":" + idAudio)

def eliminarSegundosReproduciodosAudio(r, idAudio):
    r.delete(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO + ":" + idAudio)

def getKeysSegundosReproducidosAudios(r):
    return r.keys(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO + ":*")
