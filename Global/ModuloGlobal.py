import redis
import Configuracion.constantesPrefijosClaves as constantes
import DAOS.daoGlobal as daoGlobal
import datetime

def getTotalSegundosReproducidosAudio(r, weekday):
    segundosTotales = 0
    audios = daoGlobal.getKeysSegundosReproducidosAudios(r, weekday)
    for audio in audios:
        segundosTotales += int(getSongSecondsDia(r, audio, weekday))
    return segundosTotales

def addSecondsToSong(r, idAudio, segundos):
    dt = datetime.datetime.now()
    wd = dt.weekday()

    if(r.exists(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO + ":" + str(wd)) == 0):
        daoGlobal.setSegundosReproduciodosAudio(r, idAudio, segundos, wd)
        r.expire(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO + ":" + str(wd), 604800) # expira en 7 dias
        return

    segundosActuales = int(daoGlobal.getSegundosReproduciodosAudio(r, idAudio, wd)) + int(segundos)
    daoGlobal.setSegundosReproduciodosAudio(r, idAudio, segundosActuales, wd)
    

def getSongSecondsDia(r, idAudio, weekday):
    segundos = daoGlobal.getSegundosReproduciodosAudio(r, idAudio, weekday)
    if(segundos == None):
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

