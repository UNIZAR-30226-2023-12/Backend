import requests
import redis

r = redis.Redis(host='localhost', port=6379, db=0, username='melodia', password ='melodia_Proyecto_Software_Grupo_12')


urlFlushDB = 'http://127.0.0.1:8081/FlushDB/'
urlSetUser = 'http://127.0.0.1:8081/SetUser/'
urlSetSong = 'http://127.0.0.1:8081/SetSong/'
urlValidateUser = 'http://127.0.0.1:8081/ValidateUser/'
urlSetLista = 'http://127.0.0.1:8081/SetLista/'
urlChangeNameListRepUsr = 'http://127.0.0.1:8081/ChangeNameListRepUsr/'
urlSetSongLista = 'http://127.0.0.1:8081/SetSongLista/'


#Pruebas set user

usuarioCorrecto1 = {
    'email': 'admin@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin'
}
usuarioCorrecto2 = {
    'email': 'admin2@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin'
}

usuarioMismoEmail = {
    'email': 'admin@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin'
}

usuarioDatosErroneos = {
    'email': 'admin3@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin',
    'asdf': 'asdf'
}


usuarioTipoErroneo = {
    'email': 'admin3@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'erroneo',
}

requests.post(urlFlushDB)
print("Pruebas set user")
print(requests.post(urlSetUser, json=usuarioCorrecto1).status_code)
print(requests.post(urlSetUser, json=usuarioCorrecto2).status_code)
print(requests.post(urlSetUser, json=usuarioMismoEmail).status_code)
print(requests.post(urlSetUser, json=usuarioDatosErroneos).status_code)
print(requests.post(urlSetUser, json=usuarioTipoErroneo).status_code)

# Pruebas validateUser
validateUser = {
    'email': 'admin@melodia.es',
    'contrasenya': '1234'
}

validateUserEmailErroneo = {
    'email': 'asdf',
    'contrasenya' : '1234'
}

validateUserContrasenyaErronea = {
    'email': 'admin@melodia.es',
    'contrasenya' : 'asdf'
}

validateUserDatosErroneos = {
}
validateUserDatosErroneos2 = {
    'emasil': 'as'
}


print("Pruebas validateUser")
print(requests.post(urlValidateUser, json=validateUser).json())
print(requests.post(urlValidateUser, json=validateUserEmailErroneo).status_code)
print(requests.post(urlValidateUser, json=validateUserContrasenyaErronea).status_code)
print(requests.post(urlValidateUser, json=validateUserDatosErroneos).status_code)
print(requests.post(urlValidateUser, json=validateUserDatosErroneos2).status_code)


# Pruebas  SetLista

setLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'publica',
    'tipoLista' : 'listaReproduccion'
}

setLista2 = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'publica',
    'tipoLista' : 'listaReproduccion'
}

setListaErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'nombreLista': 'lista POP',
    'privada' : 'publica',
    'tipoLista' : 'listaReproduccion'
}

setListaErrorUsuario = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'publica',
    'tipoLista' : 'listaReproduccion'
}

setListaErrorTipo = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'publica',
    'tipoLista' : 'listaRara'
}

setListaPrivacidadErronea = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'asdf',
    'tipoLista' : 'listaReproduccion'
}

setListaErrorParametros = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'asdf',
    'tipoLista' : 'listaReproduccion',
    'asdf' : 'asdf'
}

print("Pruebas SetLista")
print(requests.post(urlSetLista, json=setLista).status_code)
print(requests.post(urlSetLista, json=setLista2).status_code)
print(requests.post(urlSetLista, json=setListaErrorContrasenya).status_code)
print(requests.post(urlSetLista, json=setListaErrorUsuario).status_code)
print(requests.post(urlSetLista, json=setListaErrorTipo).status_code)
print(requests.post(urlSetLista, json=setListaPrivacidadErronea).status_code)
print(requests.post(urlSetLista, json=setListaErrorParametros).status_code)

# Pruebas ChangeNameListRepUsr


changeNameListRepUsr = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'nombreLista': 'lista ROCK'
}

changeNameListRepUsrUserErroneo = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'nombreLista': 'lista ROCK'
}

changeNameListRepUsrContrasenyaErronea = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idLista': 'lista:3',
    'nombreLista': 'lista ROCK'
}

changeNameListRepUsrListaErronea = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:6',
    'nombreLista': 'lista ROCK'
}

changeNameListRepUsrListaForbidden = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'nombreLista': 'lista ROCK'
}

print("Pruebas ChangeNameListRepUsr")
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsr).status_code)
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsrUserErroneo).status_code)
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsrContrasenyaErronea).status_code)
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsrListaErronea).status_code)
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsrListaForbidden).status_code)

# Pruebas SetSongLista
setSongLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

setSongListaForbidden = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

r.set('audio:1', 'audio:1')

print("Pruebas SetSongLista")
print(requests.post(urlSetSongLista, json=setSongLista).status_code)
print(requests.post(urlSetSongLista, json=setSongListaForbidden).status_code)