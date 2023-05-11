import redis
import Configuracion.constantesPrefijosClaves as constantes
import DAOS.daoGlobal as daoGlobal
from datetime import datetime

def getTotalSegundosReproducidosAudio(r):
    segundosTotales = 0
    keys = daoGlobal.getKeysSegundosReproducidosAudios(r)
    for key in keys:
        segundos = daoGlobal.getSegundosReproduciodosAudio(r, key)
        segundosTotales += int(segundos)
    
    return segundosTotales

def addSecondsToSong(r, idAudio, segundos):
    segundosActuales = daoGlobal.getSegundosReproduciodosAudio(r, idAudio)
    if segundosActuales is None:
        segundosActuales = 0
    segundos += int(segundosActuales)
    daoGlobal.setSegundosReproduciodosAudio(r, idAudio, segundos)

def getSongSeconds(r, idAudio):
    return daoGlobal.getSegundosReproduciodosAudio(r, idAudio)
