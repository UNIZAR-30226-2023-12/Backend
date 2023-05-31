import recomendador.generacion_datos as data_gen

import tensorflow as tf
from tensorflow import keras
import numpy as np


def orderAudios(r, idUsr, audios):

    # Cargar el recomendador
    recomendador = keras.models.load_model("recomendador/modelo_recomendador.h5")
    

    ############## Obtener las predicciones de los audios ##############
    predicciones = []

    for audio in audios:
        paquete_datos = data_gen.get_state_for_prediction(r, idUsr, audio)
        paquete_temporal = data_gen.get_audio_prediction_temporal(r, idUsr)

        input = [paquete_datos, paquete_temporal]

        prediccion = recomendador.predict(input)

        predicciones.append(prediccion)


    ############## Ordenar los audios por valoración ##############

    # pair the elements of the two lists
    pairs = list(zip(audios, predicciones))

    # sort the pairs based on the values in the second list (i.e. b)
    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    # extract the first element of each pair (i.e. the elements of a) into a new list
    audios_ordenados = [pair[0] for pair in sorted_pairs]

    return audios_ordenados

def train_model(conn, nuevo_modelo=False):
    # Carga los datos de entrenamiento, 
    # cada Xtr compuesto por una pareja 
    # [información del audio actual, información de los audios anteriores]
    Xtr, Xtr_temporal, ytr = data_gen.get_training_data(conn)

    ################  CREACIÓN DEL MODELO  ################

    if (nuevo_modelo):
        input_shape_actual = np.shape(Xtr)[1:]              # [información actual del ejemplo] 
        input_shape_temporal = np.shape(Xtr_temporal)[1:]   # [información temporal del ejemplo]

        ########## Capas de entrada ##########
        capa_actual = keras.models.Sequential([
            keras.layers.InputLayer(input_shape=input_shape_actual),
            keras.layers.Dense(8, activation="relu"),
            keras.layers.Dense(4, activation="relu"),  
        ])

        capa_temporal = keras.models.Sequential([
            keras.layers.InputLayer(input_shape=input_shape_temporal),
            keras.layers.LSTM(4)
        ])


        ########## Capas de salida ##########
        capa_combinada = keras.layers.concatenate([capa_actual.output, capa_temporal.output])

        capa_salida = keras.models.Sequential([
            # Expansión de la capa combinada
            keras.layers.Dense(4, activation="relu"),

            # Capa de salida
            keras.layers.Dense(1, activation="sigmoid")

        ])(capa_combinada)


        model = keras.Model(inputs=[capa_actual.input, capa_temporal.input], outputs=capa_salida)
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", "Recall"])
    else:
        # Cargar el recomendador
        model = keras.models.load_model("recomendador/modelo_recomendador.h5")

    model.fit([Xtr, Xtr_temporal], ytr, epochs=10)

    model.save("recomendador/modelo_recomendador.h5")


