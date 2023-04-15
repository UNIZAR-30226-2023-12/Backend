import redis
import Configuracion.constantesPrefijosClaves as constantes
import DAOS.daoGlobal as daoGlobal

def getTotalSegundosReproducidosAudio(r):
    segundosTotales = 0
    keys = daoGlobal.getKeysSegundosReproducidosAudios(r)
    for key in keys:
        segundosTotales += daoGlobal.getSegundosReproduciodosAudio(r, key)
    
    return segundosTotales

def addSecondsToSong(r, idAudio, segundos):
    segundosActuales = daoGlobal.getSegundosReproduciodosAudio(r, idAudio)
    if segundosActuales is None:
        segundosActuales = 0
    daoGlobal.setSegundosReproduciodosAudio(r, idAudio, segundosActuales + segundos)