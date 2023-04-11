import generacion_datos as data_gen

import tensorflow as tf
from tensorflow import keras
import numpy as np


def create_model(conn):
    # Carga los datos de entrenamiento
    Xtr, ytr = data_gen.get_training_data(conn)

    #############  CREACIÓN DEL MODELO  #############

    capa_entrada_actual = keras.models.Sequential([
        keras.layers.Dense(3, input_shape=(Xtr.shape[1], Xtr.shape[2]), activation="relu"),
        keras.layers.Dense(3, activation="relu"),
    ])
