import Audios.DAOs.daoAudio
import pytest

def test_guardarCancion():
    assert (Audios.DAOs.daoAudio.guardarCancion(canc) == 0)

def test_cambiarNombreCancion():
    nombreCancion = "PRUEBA"
    assert (Audios.DAOs.daoAudio.cambiarNombreCancion(1, nombreCancion) == 0)
    assert (Audios.DAOs.daoAudio.obtenerNombreCancion(1) == nombreCancion)

def test_cambiarArtistaCancion():
    artista = "ARTISTA DE PRUEBA"
    assert(Audios.DAOs.daoAudio.cambiarArtistaCancion(1, artista) == 0)
    assert(Audios.DAOs.daoAudio.obtenerArtistaCancion(1) == artista)

def test_cambiarCalidadCancion():
    calidad = 1
    assert(Audios.DAOs.daoAudio.cambiarCalidadCancion(1, calidad) == 0)
    assert(Audios.DAOs.daoAudio.obtenerCalidad(1) == calidad)

def test_cambiarVecesReproducidasCancion():
    veces = 150
    assert(Audios.DAOs.daoAudio.cambiarVecesreproducidasCancion(1, veces) == 0)
    assert(Audios.DAOs.daoAudio.obtenerVecesreproducidasCancion(1) == veces)

def test_cambiarValCancion():
    valoracion = 2
    assert(Audios.DAOs.daoAudio.cambiarValCancion(1, valoracion) == 0)
    assert(Audios.DAOs.daoAudio.obtenerValCancion(1) == valoracion)
    