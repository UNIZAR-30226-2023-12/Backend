import recomendador.generacion_datos as data_gen

import tensorflow as tf
from tensorflow import keras
import numpy as np


def create_model(conn):
    # Carga los datos de entrenamiento, 
    # cada Xtr compuesto por una pareja 
    # [información del audio actual, información de los audios anteriores]
    Xtr, ytr = data_gen.get_training_data(conn)
    
    print("Xtr shape: ", np.shape(Xtr))
    print("ytr shape: ", np.shape(ytr))

    print("Xtr[0, 0] shape: ", np.shape(Xtr[0][0]))
    print("Xtr[0, 1] shape: ", np.shape(Xtr[0][1]))

    print(Xtr[0][0])
    print(Xtr[0][1])

    
    ################  CREACIÓN DEL MODELO  ################

    input_shape_actual = np.shape(Xtr[0][0]) # [Ejemplo inicial, información actual del ejemplo] 
    input_shape_temporal = np.shape(Xtr[0][1]) # [Ejemplo inicial, información temporal del ejemplo]


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
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", "recall"])

    model.fit(Xtr, ytr, epochs=10)

