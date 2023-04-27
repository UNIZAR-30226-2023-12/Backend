import requests
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

url = 'http://127.0.0.1:8081/SetUser/'
urlValidateUser = 'http://127.0.0.1:8081/ValidateUser/'

#Pruebas set user

nuevoUsuario = {
    'email': 'admin@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin'
}
nuevoUsuario2 = {
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
    'email': 'admin@melodia.es',
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

print("Pruebas set user")
print(requests.post(url, json=nuevoUsuario).status_code)
print(requests.post(url, json=nuevoUsuario2).status_code)
print(requests.post(url, json=usuarioMismoEmail).status_code)
print(requests.post(url, json=usuarioDatosErroneos).status_code)
print(requests.post(url, json=usuarioTipoErroneo).status_code)


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

r.flushall()
print("Pruebas validateUser")
print(requests.post(urlValidateUser, json=validateUser).status_code)
print(requests.post(urlValidateUser, json=validateUserEmailErroneo).status_code)
print(requests.post(urlValidateUser, json=validateUserContrasenyaErronea).status_code)
print(requests.post(urlValidateUser, json=validateUserDatosErroneos).status_code)
print(requests.post(urlValidateUser, json=validateUserDatosErroneos2).status_code)

# Pruebas  SetLista
urlSetLista = 'http://127.0.0.1:8081/SetLista/'
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

setListaErrorTipo = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreLista': 'lista POP',
    'privada' : 'publica',
    'tipoLista' : 'listaRara'
}

print("Pruebas SetLista")
print(requests.post(urlSetLista, json=setLista).status_code)
print(requests.post(urlSetLista, json=setListaErrorTipo).status_code)

# Pruebas ChangeNameListRepUsr
urlChangeNameListRepUsr = 'http://127.0.0.1:8081/ChangeNameListRepUsr/'


changeNameListRepUsrError = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:4',
    'nombreLista': 'lista ROCK'
}
changeNameListRepUsr = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'nombreLista': 'lista ROCK'
}

print("Pruebas ChangeNameListRepUsr")
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsr).status_code)
print(requests.post(urlChangeNameListRepUsr, json=changeNameListRepUsrError).status_code)

# Pruebas SetSongLista
urlSetSongLista = 'http://127.0.0.1:8081/SetSongLista/'
setSongLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

setSongLista = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

print("Pruebas SetSongLista")
print(requests.post(urlSetSongLista, json=setSongLista).status_code)