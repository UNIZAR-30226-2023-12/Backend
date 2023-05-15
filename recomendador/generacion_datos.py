from Usuarios import usuarios
from Audios import controlAudios as audios
from Audios import moduloAudios as modAudios
from Configuracion import constantesPrefijosClaves as conf
import numpy as np
from DAOS import daoGlobal



# Almacena una nueva entrada de entrenamiento del usuario
def store_training_example(conn, id_usr, id_audio, output):

    # Obtiene los datos de entrada actuales para la predicción
    paquete_entradas = get_audio_prediction_state(conn, id_usr, id_audio)
    
    # Construye el paquete de datos para la predicción
    paquete_prediccion = {
        "inputs": paquete_entradas,
        "output": output
    }

    # Añade el usuario a la lista de usuarios con datos de entrenamiento
    daoGlobal.add_user_with_training_data(conn, id_usr)

    # Guarda los datos de predicción en la base de datos
    daoGlobal.add_new_training_example(conn, id_usr, paquete_prediccion)



# Devuelve dos matrices numpy con usuarios por filas y ejemplos por columnas,
#   El primero los ejemplos de entradas
#   (forman una matriz 3D, (n_usuarios, n_ejemplos, n_atributos))
#
#   El segundo los ejemplos de salida (porcentaje de 0 a 1)
def get_training_data(conn):
    
    users_with_training_data = daoGlobal.get_users_with_training_data(conn) 

    #datos_entrada = np.empty((0, 2))  # Arrays con los ejemplos de entrada
    datos_entrada = np.empty((0, 72)) 
    datos_entrada_ventanas = np.empty((0, conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION,
                                        1+conf.GENERO_NUMERO_GENEROS))
    datos_salida = np.empty((0))   # Arrays con las salidas de cada ejemplo

    
    for id_usr in users_with_training_data:

        ############ Obtener datos de la BDD ############
        
        # Obtiene los datos de entrenamiento de la base de datos
        datos_entrenamiento = daoGlobal.get_usr_training_examples(conn, id_usr)

        # Separa los datos de entrada de los datos de salida
        datos_entrada_usr = []
        datos_salida_usr = []

        for paquete in datos_entrenamiento:

            datos_entrada_usr.append(paquete["inputs"])
            datos_salida_usr.append(paquete["output"])


        ############ Preparar datos para la red neuronal ############

        datos_entrada_usr = limpiar_datos(datos_entrada_usr)
        datos_entrada_usr = np.array(datos_entrada_usr)
        datos_salida_usr = np.array(datos_salida_usr)

        window_size = min(conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION, len(datos_entrada_usr))
        # Crea ventanas deslizantes con el histórico de cada ejemplos
        datos_temporales = np.copy(datos_entrada_usr)
        datos_temporales = limpiar_datos_temporales(datos_temporales)
        ventana_inputs_usr = sliding_window(datos_temporales, conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION)

        
        # Elimina los datos de entrenamiento iniciales para alinearlos con las ventanas
        datos_entrada_usr = datos_entrada_usr[window_size-1:] 
        datos_salida_usr = datos_salida_usr[window_size-1:]

        ############ Añadir datos a la lista de datos ############

        # Añade los datos de entrada y salida del usuario a la lista de datos
        #datos_entrada = np.append(datos_entrada, inputs_usr, axis=0)
        
        datos_entrada = np.append(datos_entrada, datos_entrada_usr, axis=0)
        datos_entrada_ventanas = np.append(datos_entrada_ventanas, ventana_inputs_usr, axis=0)
        datos_salida = np.append(datos_salida, datos_salida_usr, axis=0)

        # Elimina los datos de entrenamiento del usuario
        daoGlobal.delete_user_with_training_data(conn, id_usr)
        daoGlobal.delete_usr_training_examples(conn, id_usr)


    return datos_entrada, datos_entrada_ventanas, datos_salida
    


def limpiar_datos_temporales(datos_temporales):

    nGeneros = conf.GENERO_NUMERO_GENEROS

    n_ejemplos = np.shape(datos_temporales)[0]
    limpios = np.empty((n_ejemplos, nGeneros+1))
    
    for i in range(n_ejemplos):
        limpios[i, 0] = (datos_temporales[i, 3] == "True")      # esPodcast
        limpios[i, 1:1+nGeneros] = datos_temporales[i, 9:9+nGeneros] # Genero del audio

    return limpios



def limpiar_datos(datos_entrada_usr):
    for i in range(len(datos_entrada_usr)):
        datos_entrada_usr[i][0] = float(datos_entrada_usr[i][0])
        datos_entrada_usr[i][1] = float(datos_entrada_usr[i][1])
        datos_entrada_usr[i][2] = float(datos_entrada_usr[i][2])
        datos_entrada_usr[i][3] = float((datos_entrada_usr[i][3] == "True"))
        datos_entrada_usr[i][4] = float(datos_entrada_usr[i][4])
        datos_entrada_usr[i][5] = float(datos_entrada_usr[i][5])
        datos_entrada_usr[i][6] = float(datos_entrada_usr[i][6])
        datos_entrada_usr[i][7] = float(datos_entrada_usr[i][7])
        datos_entrada_usr[i][8] = float(datos_entrada_usr[i][8])

    return datos_entrada_usr


# Generates a sliding window of inputs and outputs and size `window_size`
def sliding_window(inputs, window_size=conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION):

    num_inputs = np.shape(inputs)[0]
    input_shape = np.shape(inputs)[1:]

    window_size = min(window_size, num_inputs)
    num_windows = max(num_inputs - window_size + 1, 1)

    # Create empty arrays to hold the sliding window data
    X = np.zeros((num_windows, window_size, *input_shape), dtype=inputs.dtype)
    #y = np.zeros((num_windows, *np.shape(outputs[0])), dtype=outputs.dtype)

    # Iterate over the sliding window and populate `X` and `y`
    for i in range(num_windows):
        X[i] = inputs[i:i+window_size, :]
        #y[i] = outputs[i+window_size-1]
        
    return X    #, y



# Captura el estado del audio para la predicción
# Siendo el estado: si el audio es favorito, el numero de reproducciones...
# Devuelve una lista de python con los datos de entrada
def get_audio_prediction_state(conn, id_usr, id_audio):

    esFavorito = usuarios.esFavorito(conn, id_usr, id_audio)        # 1 si es favorito del usuario, 0 si no
    estaGuardado = usuarios.estaGuardado(conn, id_usr, id_audio)    # 1 si esta guardado en la biblioteca del usuario, 0 si no
    es_podcast = audios.obtenerEsPodcast(conn, id_audio)            # 1 si es podcast, 0 si no

    if es_podcast:
        valoracion_media = modAudios.obtenerValMedia(conn, id_audio)           # Valoración media del audio
        n_reproducciones = audios.obtenerVecesReproducidasPodcast(conn, id_audio)    # Número de reproducciones del audio
        n_favoritos = audios.obtenerFavoritosPodcast(conn, id_audio)                 # Número de favoritos del audio
        id_genero = audios.obtenerGenerosPodcast(conn, id_audio)                     # Genero del audio, un entero
        es_podcast = 1
    else:
        valoracion_media = modAudios.obtenerValMedia(conn, id_audio)         # Valoración media del audio
        n_reproducciones = audios.obtenerVecesReproducidasCancion(conn, id_audio)  # Número de reproducciones del audio
        n_favoritos = audios.obtenerNumFavoritosCancion(conn, id_audio)            # Número de favoritos del audio
        id_genero = audios.obtenerGenCancion(conn, id_audio)                       # Genero del audio, un entero
        es_podcast = 0
        
    
    id_artista = audios.obtenerArtCancion(conn, id_audio)         # Obtiene el artista del audio
    suscrito = usuarios.isSubscribedToArtist(conn, id_usr, id_artista)    # 1 si esta suscrito, 0 si no

    # Obtiene el porcentaje de favoritos por genero del usuario
    numero_favoritos_por_genero = usuarios.getNFavoritosPorGenero(conn, id_usr) # Es una lista de enteros
    numero_favoritos_por_genero = np.array(numero_favoritos_por_genero)

    # Obtiene el porcentaje de audios favoritos de ese artista
    numero_favoritos_del_artista = usuarios.getNFavoritosPorArtista(conn, id_usr, id_artista) # Es un entero


    n_favoritos = usuarios.getNFavoritos(conn, id_usr)
    
    if n_favoritos != 0:
        porcentaje_favoritos_por_genero = numero_favoritos_por_genero / n_favoritos
        porcentaje_favoritos_del_artista = numero_favoritos_del_artista / n_favoritos
    else:
        porcentaje_favoritos_por_genero = np.zeros(len(numero_favoritos_por_genero))
        porcentaje_favoritos_del_artista = 0

    porcentaje_favoritos_por_genero = porcentaje_favoritos_por_genero.tolist()


    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    porcentaje_favoritos_por_genero_amigos = get_porcentaje_favoritos_por_genero_amigos(conn, id_usr)

    # Obtiene el porcentaje de favoritos de ese artista de los amigos del usuario
    porcentaje_favoritos_de_artista_amigos = get_porcentaje_favoritos_de_artista_amigos(conn, id_usr, id_artista)


    # Codifica el genero del audio en one hot
    generos_one_hot = np.zeros(conf.GENERO_NUMERO_GENEROS)
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


def get_state_for_prediction(r, id_usr, id_audio):
    print(get_audio_prediction_state(r, id_usr, id_audio))
    paquete_datos = np.array(get_audio_prediction_state(r, id_usr, id_audio), np.float32)
    paquete_datos = np.reshape(paquete_datos, (1, np.shape(paquete_datos)[0]))

    paquete_datos = limpiar_datos(paquete_datos)
    return np.array(paquete_datos, np.float32)




def get_audio_prediction_temporal(r, id_usr):
    paquete_temporal = np.array(daoGlobal.get_temporal_data(r, id_usr))
    nGeneros = conf.GENERO_NUMERO_GENEROS

    len_temporal = len(paquete_temporal)
    limpio = np.empty((len_temporal, nGeneros+1), np.float32)

    for i in range(len_temporal):    
        limpio[i, 0] = (paquete_temporal[i, 0] == "True")            # esPodcast

        id_genero = paquete_temporal[i, 1]
        generos_one_hot = np.zeros(conf.GENERO_NUMERO_GENEROS, np.float32)
        generos_one_hot[id_genero] = 1

        limpio[i, 1:1+nGeneros] = generos_one_hot   # Genero del audio

    limpio = np.reshape(limpio, (1, np.shape(limpio)[0], np.shape(limpio)[1]))

    return limpio

def add_audio_prediction_temporal(r, id_usr, id_audio):

    es_podcast = audios.obtenerEsPodcast(r, id_audio)            # 1 si es podcast, 0 si no

    if es_podcast:
        id_genero = audios.obtenerGenerosPodcast(r, id_audio)                     # Genero del audio, un entero
    else:
        id_genero = audios.obtenerGenCancion(r, id_audio)                       # Genero del audio, un entero

    paquete_temporal = [es_podcast, id_genero]
    daoGlobal.add_temporal_data(r, id_usr, paquete_temporal)





###############################################################################
###########################  Funciones auxiliares  ############################
###############################################################################

# Devuelve una lista con el porcentaje de audios favoritos de cada genero
# de los amigos del usuario
def get_porcentaje_favoritos_por_genero_amigos(conn, id_usr):

    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    amigos = usuarios.getAmigos(conn, id_usr) # Lista con las ids de los amigos
    porcentaje_favoritos_por_genero_amigos = np.zeros(conf.GENERO_NUMERO_GENEROS)

    # Suma los favoritos por genero de todos los amigos
    for id_amigo in amigos:
        # Obtiene el numero de favoritos por genero del amigo
        temp_n_favoritos_por_genero = usuarios.getNFavoritosPorGenero(conn, id_amigo)    
        temp_n_favoritos_por_genero = np.array(temp_n_favoritos_por_genero)

        # Calcula el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos = temp_n_favoritos_por_genero / usuarios.getNFavoritos(conn, id_amigo)

        # Añade el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos_por_genero_amigos += porcentaje_favoritos


    # Calcula la media entre de los amigos
    if len(amigos) != 0:    
        porcentaje_favoritos_por_genero_amigos /= len(amigos)
    else:
        porcentaje_favoritos_por_genero_amigos = np.zeros(conf.GENERO_NUMERO_GENEROS)

    return porcentaje_favoritos_por_genero_amigos.tolist()



# Devuelve el porcentaje de audios favoritos de ese artista de los amigos del usuario
def get_porcentaje_favoritos_de_artista_amigos(conn, id_usr, id_artista):

    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    amigos = usuarios.getAmigos(conn, id_usr) # Lista con las ids de los amigos
    porcentaje_favoritos_de_artista_amigos = 0

    # Suma los favoritos por genero de todos los amigos
    for id_amigo in amigos:
        # Obtiene el numero de favoritos por genero del amigo
        temp_numero_favoritos_del_artista_amigo = usuarios.getNFavoritosPorArtista(conn, id_amigo, id_artista) # Es un entero
        
        # Calcula el porcentaje de favoritos por genero del amigo
        favAmigos = usuarios.getNFavoritos(conn, id_amigo)
        porcentaje_favoritos = 0
        if favAmigos != 0:
            porcentaje_favoritos = temp_numero_favoritos_del_artista_amigo / usuarios.getNFavoritos(conn, id_amigo)

        # Añade el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos_de_artista_amigos += porcentaje_favoritos

    # Calcula la media entre de los amigos
    if len(amigos) != 0:
        porcentaje_favoritos_de_artista_amigos /= len(amigos)
    else:
        porcentaje_favoritos_de_artista_amigos = 0

    return porcentaje_favoritos_de_artista_amigos