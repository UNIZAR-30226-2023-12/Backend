import redis
import Configuracion.constantesPrefijosClaves as constantes
import json

def add_user_with_training_data(r, id_usr):
    r.sadd(constantes.CLAVE_SET_USUARIOS_ENTRENADOS, id_usr)

def delete_user_with_training_data(r, id_usr):
    r.srem(constantes.CLAVE_SET_USUARIOS_ENTRENADOS, id_usr)

def get_users_with_training_data(r):
    return r.smembers(constantes.CLAVE_SET_USUARIOS_ENTRENADOS)



def add_new_training_example(r, id_usr, paquete_datos):
    r.rpush(constantes.CLAVE_LISTA_ENTRENAMIENTO+":"+ str(id_usr), json.dumps(paquete_datos))

def get_usr_training_examples(r, id_usr):
    list = r.lrange(constantes.CLAVE_LISTA_ENTRENAMIENTO+":"+ str(id_usr), 0, -1)

    for i in range(len(list)):
        list[i] = json.loads(list[i])

    return list

def delete_usr_training_examples(r, id_usr):
    r.delete(constantes.CLAVE_LISTA_ENTRENAMIENTO+":"+ str(id_usr))