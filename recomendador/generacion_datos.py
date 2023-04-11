from Usuarios import usuarios
from Audios import controlAudios as audios
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

    datos_entrada = np.empty()  # Arrays con los ejemplos de entrada
    datos_salida = np.empty()   # Arrays con las salidas de cada ejemplo

    
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

        # Crea ventanas deslizantes con el histórico de cada ejemplos
        datos_temporales = np.copy(datos_entrada_usr)
        datos_temporales = limpiar_datos_temporales(datos_temporales)
        ventana_inputs_usr, ventana_outputs_usr = sliding_window(datos_temporales, datos_salida_usr, conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION)

        # Elimina los datos de entrenamiento iniciales para alinearlos con las ventanas
        datos_entrada_usr = datos_entrada_usr[conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION-1:] 
        datos_salida_usr = datos_salida_usr[conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION-1:]

        # Hace un zip de los datos con las ventanas
        inputs_usr = zip(datos_entrada_usr, ventana_inputs_usr)
        outputs_usr = zip(datos_salida_usr, ventana_outputs_usr)
        

        ############ Añadir datos a la lista de datos ############
        
        # Añade los datos de entrada y salida del usuario a la lista de datos
        datos_entrada = np.append(datos_entrada, inputs_usr)
        datos_salida = np.append(datos_salida, outputs_usr)

        # Elimina los datos de entrenamiento del usuario
        daoGlobal.delete_user_with_training_data(conn, id_usr)
        daoGlobal.delete_usr_training_examples(conn, id_usr)


    return datos_entrada, datos_salida
    


def limpiar_datos_temporales(datos_temporales):

    nGeneros = conf.GENERO_NUMERO_GENEROS

    limpios = np.empty((nGeneros+1, np.shape(datos_temporales)[1]))

    limpios[:, 0] = datos_temporales[:, 3]      # esPodcast
    limpios[:, 1:1+nGeneros] = datos_temporales[:, 9:9+nGeneros] # Genero del audio

    return limpios



# Generates a sliding window of inputs and outputs and size `window_size`
def sliding_window(inputs, outputs, window_size=conf.RECOMENDADOR_TAMANYO_VENTANA_PREDICCION):

    num_inputs, *input_shape = inputs.shape
    num_windows = num_inputs - window_size + 1
    
    # Create empty arrays to hold the sliding window data
    X = np.zeros((num_windows, window_size, *input_shape), dtype=inputs.dtype)
    y = np.zeros((num_windows, *outputs[0].shape), dtype=outputs.dtype)

    # Iterate over the sliding window and populate `X` and `y`
    for i in range(num_windows):
        X[i] = inputs[i:i+window_size]
        y[i] = outputs[i+window_size-1]
        
    return X, y



# Captura el estado del audio para la predicción
# Siendo el estado: si el audio es favorito, el numero de reproducciones...
# Devuelve una lista de python con los datos de entrada
def get_audio_prediction_state(conn, id_usr, id_audio):

    esFavorito = usuarios.esFavorito(conn, id_usr, id_audio)        # 1 si es favorito del usuario, 0 si no
    estaGuardado = usuarios.estaGuardado(conn, id_usr, id_audio)    # 1 si esta guardado en la biblioteca del usuario, 0 si no
    es_podcast = audios.obtenerEsPodcast(conn, id_audio)            # 1 si es podcast, 0 si no

    if es_podcast:
        valoracion_media = audios.obtenerValoracionPodcast(conn, id_audio)           # Valoración media del audio
        n_reproducciones = audios.obtenerVecesReproducidasPodcast(conn, id_audio)    # Número de reproducciones del audio
        n_favoritos = audios.obtenerFavoritosPodcast(conn, id_audio)                 # Número de favoritos del audio
        id_genero = audios.obtenerGenerosPodcast(conn, id_audio)                     # Genero del audio, un entero

    else:
        valoracion_media = audios.obtenerValoracionCancion(conn, id_audio)         # Valoración media del audio
        n_reproducciones = audios.obtenerVecesReproducidasCancion(conn, id_audio)  # Número de reproducciones del audio
        n_favoritos = audios.obtenerNumFavoritosCancion(conn, id_audio)            # Número de favoritos del audio
        id_genero = audios.obtenerGenCancion(conn, id_audio)                       # Genero del audio, un entero


    id_artista = audios.obtenerArtCancion(conn, id_audio)         # Obtiene el artista del audio
    suscrito = usuarios.estaSuscrito(conn, id_usr, id_artista)    # 1 si esta suscrito, 0 si no

    # Obtiene el porcentaje de favoritos por genero del usuario
    numero_favoritos_por_genero = usuarios.getNFavoritosPorGenero(conn, id_usr) # Es una lista de enteros
    numero_favoritos_por_genero = np.array(numero_favoritos_por_genero)
    porcentaje_favoritos_por_genero = numero_favoritos_por_genero / usuarios.getNFavoritos(conn, id_usr)
    porcentaje_favoritos_por_genero = porcentaje_favoritos_por_genero.tolist()

    # Obtiene el porcentaje de favoritos por genero de los amigos del usuario
    porcentaje_favoritos_por_genero_amigos = get_porcentaje_favoritos_por_genero_amigos(conn, id_usr)


    # Obtiene el porcentaje de audios favoritos de ese artista
    numero_favoritos_del_artista = usuarios.getNFavoritosPorArtista(conn, id_usr, id_artista) # Es un entero
    porcentaje_favoritos_del_artista = numero_favoritos_del_artista / usuarios.getNFavoritos(conn, id_usr)

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
    porcentaje_favoritos_por_genero_amigos /= len(amigos)

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
        porcentaje_favoritos = temp_numero_favoritos_del_artista_amigo / usuarios.getNFavoritos(conn, id_amigo)

        # Añade el porcentaje de favoritos por genero del amigo
        porcentaje_favoritos_de_artista_amigos += porcentaje_favoritos

    # Calcula la media entre de los amigos
    porcentaje_favoritos_de_artista_amigos /= len(amigos)

    return porcentaje_favoritos_de_artista_amigos