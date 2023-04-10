from Usuarios import usuarios
from Audios import controlAudios as audios
from Configuracion import constantesPrefijosClaves as conf
import numpy as np
from DAOS import daoGlobal



# Almacena una nueva entrada de entrenamiento del usuario
def store_training_example(id_usr, id_audio, output):

    # Obtiene los datos de entrada actuales para la predicción
    paquete_entradas = get_audio_prediction_state(id_usr, id_audio)

    # Construye el paquete de datos para la predicción
    paquete_prediccion = {
        "inputs": paquete_entradas,
        "output": output
    }

    # Añade el usuario a la lista de usuarios con datos de entrenamiento
    daoGlobal.add_user_with_training_data(id_usr)

    # Guarda los datos de predicción en la base de datos
    daoGlobal.add_new_training_example(id_usr, paquete_prediccion)



# Devuelve dos matrices numpy con usuarios por filas y ejemplos por columnas,
#   El primero los ejemplos de entradas
#   (forman una matriz 3D, (n_usuarios, n_ejemplos, n_atributos))
#
#   El segundo los ejemplos de salida (porcentaje de 0 a 1)
def get_training_data():
    
    users_with_training_data = daoGlobal.get_users_with_training_data() 

    datos_entrada = np.empty()
    datos_salida = np.empty()
    
    for id_usr in users_with_training_data:
        # Obtiene los datos de entrenamiento de la base de datos
        datos_entrenamiento = daoGlobal.get_usr_training_examples(id_usr)

        # Separa los datos de entrada de los datos de salida
        datos_entrada_usr = []
        datos_salida_usr = []

        for paquete in datos_entrenamiento:
            datos_entrada_usr.append(paquete["inputs"])
            datos_salida_usr.append(paquete["output"])

        # Añade los datos de entrada y salida del usuario a la lista de datos
        datos_entrada = np.stack(datos_entrada, datos_entrada_usr)
        datos_salida = np.stack(datos_salida, datos_salida_usr)

        # Elimina los datos de entrenamiento del usuario
        daoGlobal.delete_user_with_training_data(id_usr)
        daoGlobal.delete_usr_training_examples(id_usr)

    return datos_entrada, datos_salida
    


# Captura el estado del audio para la predicción
# Siendo el estado: si el audio es favorito, el numero de reproducciones...
# Devuelve una lista de python con los datos de entrada
def get_audio_prediction_state(id_usr, id_audio):

    esFavorito = usuarios.esFavorito(id_usr, id_audio)        # 1 si es favorito del usuario, 0 si no
    estaGuardado = audios.estaGuardado(id_usr, id_audio)    # 1 si esta guardado en la biblioteca del usuario, 0 si no
    valoracion_media = audios.getValoracionMedia(id_audio)  # Valoración media del audio
    es_podcast = audios.esPodcast(id_audio)                 # 1 si es podcast, 0 si no
    n_reproducciones = audios.getNReproducciones(id_audio)  # Número de reproducciones del audio
    n_favoritos = audios.getNFavoritos(id_audio)            # Número de favoritos del audio

    id_artista = audios.getArtista(id_audio)
    suscrito = usuarios.suscrito(id_usr, id_artista)    # 1 si esta suscrito, 0 si no

    # Obtiene el porcentaje de favoritos por genero del usuario
    numero_favoritos_por_genero = usuarios.getNFavoritosPorGenero(id_usr) # Es una lista de enteros
    numero_favoritos_por_genero = np.array(numero_favoritos_por_genero)
    porcentaje_favoritos_por_genero = numero_favoritos_por_genero / usuarios.getNFavoritos(id_usr)
    porcentaje_favoritos_por_genero = porcentaje_favoritos_por_genero.tolist()

    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    porcentaje_favoritos_por_genero_amigos = get_porcentaje_favoritos_por_genero_amigos(id_usr)


    # Obtiene el porcentaje de audios favoritos de ese artista
    numero_favoritos_del_artista = usuarios.getNFavoritosPorDelArtista(id_usr, id_artista) # Es un entero
    porcentaje_favoritos_del_artista = numero_favoritos_del_artista / usuarios.getNFavoritos(id_usr)

    # Obtiene el porcentaje de favoritos de ese artista de los amigos del usuario
    porcentaje_favoritos_de_artista_amigos = get_porcentaje_favoritos_de_artista_amigos(id_usr, id_artista)


    # Codifica el genero del audio en one hot
    id_genero = audios.getGenero(id_audio)                     # Genero del audio, un entero

    generos_one_hot = np.zeros(conf.NUMERO_GENEROS)
    generos_one_hot[id_genero] = 1
    generos_one_hot = generos_one_hot.tolist()


    # Construye el paquete de datos para la predicción
    paquete_datos =  [esFavorito, estaGuardado, 
                        valoracion_media, es_podcast, n_reproducciones, 
                        n_favoritos, suscrito, 
                        porcentaje_favoritos_del_artista,
                        porcentaje_favoritos_de_artista_amigos]
    
    # Añade el genero codificado en one hot
    paquete_datos += generos_one_hot

    # Añade las listas de porcentaje de favoritos por genero
    paquete_datos += porcentaje_favoritos_por_genero
    paquete_datos += porcentaje_favoritos_por_genero_amigos

    return paquete_datos




###############################################################################
###########################  Funciones auxiliares  ############################
###############################################################################

# Devuelve una lista con el porcentaje de audios favoritos de cada genero
# de los amigos del usuario
def get_porcentaje_favoritos_por_genero_amigos(id_usr):

    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    amigos = usuarios.getAmigos(id_usr) # Lista con las ids de los amigos
    porcentaje_favoritos_por_genero_amigos = np.zeros(conf.NUMERO_GENEROS)

    # Suma los favoritos por genero de todos los amigos
    for id_amigo in amigos:
        # Obtiene el numero de favoritos por genero del amigo
        temp_n_favoritos_por_genero = usuarios.getNFavoritosPorGenero(id_amigo)    
        temp_n_favoritos_por_genero = np.array(temp_n_favoritos_por_genero)

        # Calcula el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos = temp_n_favoritos_por_genero / usuarios.getNFavoritos(id_amigo)

        # Añade el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos_por_genero_amigos += porcentaje_favoritos

    # Calcula la media entre de los amigos
    porcentaje_favoritos_por_genero_amigos /= len(amigos)

    return porcentaje_favoritos_por_genero_amigos.tolist()



# Devuelve el porcentaje de audios favoritos de ese artista de los amigos del usuario
def get_porcentaje_favoritos_de_artista_amigos(id_usr, id_artista):

    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    amigos = usuarios.getAmigos(id_usr) # Lista con las ids de los amigos
    porcentaje_favoritos_de_artista_amigos = 0

    # Suma los favoritos por genero de todos los amigos
    for id_amigo in amigos:
        # Obtiene el numero de favoritos por genero del amigo
        temp_numero_favoritos_del_artista_amigo = usuarios.getNFavoritosPorDelArtista(id_amigo, id_artista) # Es un entero
        
        # Calcula el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos = temp_numero_favoritos_del_artista_amigo / usuarios.getNFavoritos(id_amigo)

        # Añade el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos_de_artista_amigos += porcentaje_favoritos

    # Calcula la media entre de los amigos
    porcentaje_favoritos_de_artista_amigos /= len(amigos)

    return porcentaje_favoritos_de_artista_amigos