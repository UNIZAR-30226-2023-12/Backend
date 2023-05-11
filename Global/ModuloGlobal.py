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
    if(r.exists(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO) == 0):
        daoGlobal.setSegundosReproduciodosAudio(r, idAudio, segundos)
        segundosExpire = getTimeUntilSunday()
        r.expire(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO, segundosExpire)
        return

    segundosActuales = daoGlobal.getSegundosReproduciodosAudio(r, idAudio)
    if segundosActuales is None:
        segundosActuales = 0
    segundos += int(segundosActuales)
    daoGlobal.setSegundosReproduciodosAudio(r, idAudio, segundos)

def getSongSeconds(r, idAudio):
    segundos = daoGlobal.getSegundosReproduciodosAudio(r, idAudio)
    if segundos is None:
        return 0
    return segundos

# Funcion interna para obtener el numero de segundos que faltan hasta el domingo
def getTimeUntilSunday():
    dt = datetime.datetime.now()
    x = dt.weekday()
    tomorrow = dt + datetime.timedelta(days=7 - x)
    time = datetime.datetime.combine(tomorrow, datetime.time.min) - dt
    segundos = time.total_seconds()
    segundos = int(segundos)
    return segundos

