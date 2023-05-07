import redis
import Configuracion.constantesPrefijosClaves as constantes
import json

def add_user_with_training_data(r, id_usr):
    r.sadd(constantes.CLAVE_SET_USUARIOS_ENTRENADOS, id_usr)

def delete_user_with_training_data(r, id_usr):
    r.srem(constantes.CLAVE_SET_USUARIOS_ENTRENADOS, id_usr)

def get_users_with_training_data(r):
    return r.smembers(constantes.CLAVE_SET_USUARIOS_ENTRENADOS)


# Obtiene datos sobre la sesión del usuario para el recomendador
def get_temporal_data(r, id_usr):
    list = r.lrange(constantes.CLAVE_TEMPORAL_ENTRENAMIENTO+":"+ str(id_usr), 0, -1)

    for i in range(len(list)):
        list[i] = json.loads(list[i])

    return list

# Añade datos de sesión del usuario para el recomendador
def add_temporal_data(r, id_usr, paquete_datos):
    r.rpush(constantes.CLAVE_TEMPORAL_ENTRENAMIENTO+":"+ str(id_usr), json.dumps(paquete_datos))

    # Si la lista tiene más de RECOMENDADOR_TAMANYO_VENTANA_PREDICCION elementos, elimina el más antiguo
    if r.llen(constantes.CLAVE_TEMPORAL_ENTRENAMIENTO+":"+ str(id_usr)) > constantes.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION:
        r.lpop(constantes.CLAVE_TEMPORAL_ENTRENAMIENTO+":"+ str(id_usr))


def add_new_training_example(r, id_usr, paquete_datos):
    r.rpush(constantes.CLAVE_LISTA_ENTRENAMIENTO+":"+ str(id_usr), json.dumps(paquete_datos))

def get_usr_training_examples(r, id_usr):
    list = r.lrange(constantes.CLAVE_LISTA_ENTRENAMIENTO+":"+ str(id_usr), 0, -1)

    for i in range(len(list)):
        list[i] = json.loads(list[i])

    return list

def delete_usr_training_examples(r, id_usr):
    r.delete(constantes.CLAVE_LISTA_ENTRENAMIENTO+":"+ str(id_usr))

# Daos para las estadisitcas de segundos reproducidos de los audios
def setSegundosReproduciodosAudio(r, idAudio, segundos):
    r.hset(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO, idAudio, segundos)

def getSegundosReproduciodosAudio(r, idAudio):
    return r.hget(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO, idAudio)

def eliminarSegundosReproduciodosAudio(r, idAudio):
    r.hdel(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO, idAudio)

def getKeysSegundosReproducidosAudios(r):
    return r.hkeys(constantes.PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO)
