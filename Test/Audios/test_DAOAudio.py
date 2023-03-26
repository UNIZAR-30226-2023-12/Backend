from Audios import daoAudio
from Usuarios import daoUsuario
from Global import daoGlobal
import pytest
import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def test_guardarCancion():
    assert (daoAudio.guardarCancion(r, canc) == 0)

def test_cambiarNombreCancion():
    nombreCancion = "PRUEBA"
    assert (daoAudio.cambiarNombreCancion(r, 1, nombreCancion) == 0)
    assert (daoAudio.obtenerNombreCancion(r, 1) == nombreCancion)

def test_cambiarArtistaCancion():
    artista = "ARTISTA DE PRUEBA"
    assert(daoAudio.cambiarArtistaCancion(r, 1, artista) == 0)
    assert(daoAudio.obtenerArtistaCancion(r, 1) == artista)

def test_cambiarCalidadCancion():
    calidad = 1
    assert(daoAudio.cambiarCalidadCancion(r, 1, calidad) == 0)
    assert(daoAudio.obtenerCalidad(r, 1) == calidad)

def test_cambiarVecesReproducidasCancion():
    veces = 150
    assert(daoAudio.cambiarVecesreproducidasCancion(r, 1, veces) == 0)
    assert(daoAudio.obtenerVecesreproducidasCancion(1) == veces)

def test_cambiarValCancion():
    valoracion = 2
    assert(daoAudio.cambiarValCancion(r, 1, valoracion) == 0)
    assert(daoAudio.obtenerValCancion(r, 1) == valoracion)
    