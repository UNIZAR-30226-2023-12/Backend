import requests
import redis

r = redis.Redis(host='localhost', port=6379, db=0, username='melodia', password ='melodia_Proyecto_Software_Grupo_12')


urlFlushDB = 'http://127.0.0.1:8081/FlushDB/'
urlSetUser = 'http://127.0.0.1:8081/SetUser/'
urlGetUser = 'http://127.0.0.1:8081/GetUser/'
urlSetSong = 'http://127.0.0.1:8081/SetSong/'
urlValidateUser = 'http://127.0.0.1:8081/ValidateUser/'
urlSetLista = 'http://127.0.0.1:8081/SetLista/'
urlChangeNameListRepUsr = 'http://127.0.0.1:8081/ChangeNameListRepUsr/'
urlSetSongLista = 'http://127.0.0.1:8081/SetSongLista/'
urlGetLista = 'http://127.0.0.1:8081/GetLista/'
urlGetListasUsr = 'http://127.0.0.1:8081/GetListasUsr/'
urlGetAudiosLista = 'http://127.0.0.1:8081/GetAudiosLista/'
urlRemoveSongLista = 'http://127.0.0.1:8081/RemoveSongLista/'
urlAskAdminToBeArtist = 'http://127.0.0.1:8081/AskAdminToBeArtist/'
urlAcceptArtist = 'http://127.0.0.1:8081/AcceptArtist/'
urlGetTotRepTime = 'http://127.0.0.1:8081/GetTotRepTime/'
urlAddSecondsToSong = 'http://127.0.0.1:8081/AddSecondsToSong/'
urlSetFolder = 'http://127.0.0.1:8081/SetFolder/'
urlAddListToFolder = 'http://127.0.0.1:8081/AddListToFolder/'


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

# Pruebas GetUser
getUser = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

getUserErroneo = {
    'idUsr': 'usuario:4',
    'contrasenya': '1234'
}

getUserContrasenyaErronea = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345'
}

print("Pruebas get user")
print(requests.post(urlGetUser, json=getUser).json())
print(requests.post(urlGetUser, json=getUserErroneo).status_code)
print(requests.post(urlGetUser, json=getUserContrasenyaErronea).status_code)


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
    'privada' : 'privada',
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

setSongListaErrorUsuario = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

setSongListaErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

setSongListaErrorLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:6',
    'idAudio': 'audio:1'
}

setSongListaErrorAudio = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:2'
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
print(requests.post(urlSetSongLista, json=setSongListaErrorUsuario).status_code)
print(requests.post(urlSetSongLista, json=setSongListaErrorContrasenya).status_code)
print(requests.post(urlSetSongLista, json=setSongListaErrorLista).status_code)
print(requests.post(urlSetSongLista, json=setSongListaErrorAudio).status_code)
print(requests.post(urlSetSongLista, json=setSongListaForbidden).status_code)

# Pruebas getLista
getLista = {   
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3'
}

getListaErrorUsuario = {
    'idUsr' : 'usuario:3',
    'contrasenya' : '1234',
    'idLista' : 'lista:3'
}

getListaErrorContrasenya = {
    'idUsr' : 'usuario:1',
    'contrasenya' : '12345',
    'idLista' : 'lista:3'
}

getListaErrorLista = {
    'idUsr' : 'usuario:1',
    'contrasenya' : '1234',
    'idLista' : 'lista:6'
}

getListaForbidden = {
    'idUsr' : 'usuario:1',
    'contrasenya' : '1234',
    'idLista' : 'lista:4'
}

print("Pruebas getLista")
respuesta = requests.post(urlGetLista, json=getLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLista, json=getListaErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLista, json=getListaErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLista, json=getListaErrorLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLista, json=getListaForbidden)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas getListasUsr
getListasUsr = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

getListasUsrErrorUsuario = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234'
}

getListasUsrErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345'
}

getListasUsrPublicas = {
    'idUsr': 'usuario:2',
    'contrasenya': None
}

getListasUsrPublicas2 = {
    'idUsr': 'usuario:1',
    'contrasenya': None
}

print("Pruebas getListasUsr")
respuesta = requests.post(urlGetListasUsr, json=getListasUsr)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetListasUsr, json=getListasUsrErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetListasUsr, json=getListasUsrErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetListasUsr, json=getListasUsrPublicas)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetListasUsr, json=getListasUsrPublicas2)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas getAudiosLista
getAudiosLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3'
}

getAudiosListaErrorUsuario = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
    'idLista': 'lista:3'
}

getAudiosListaErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idLista': 'lista:3'
}

getAudiosListaErrorLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:6'
}

getAudiosListaForbidden = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:4'
}

getAudiosListaPublica = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idLista': 'lista:3'
}

print("Pruebas getAudiosLista")
respuesta = requests.post(urlGetAudiosLista, json=getAudiosLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetAudiosLista, json=getAudiosListaErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetAudiosLista, json=getAudiosListaErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetAudiosLista, json=getAudiosListaErrorLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetAudiosLista, json=getAudiosListaForbidden)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetAudiosLista, json=getAudiosListaPublica)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas RemoveSongLista

removeSongLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

removeSongListaErrorUsuario = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

removeSongListaErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}

removeSongListaErrorLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:6',
    'idAudio': 'audio:1'
}

removeSongListaErrorAudio = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:6'
}

removeSongListaAudioNotInLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:2'
}

removeSongListaForbidden = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idLista': 'lista:3',
    'idAudio': 'audio:1'
}
r.set('audio:2', 'audio2')

print("Pruebas removeSongLista")

respuesta = requests.post(urlRemoveSongLista, json=removeSongListaErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlRemoveSongLista, json=removeSongListaErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlRemoveSongLista, json=removeSongListaErrorLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlRemoveSongLista, json=removeSongListaErrorAudio)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlRemoveSongLista, json=removeSongListaAudioNotInLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlRemoveSongLista, json=removeSongListaForbidden)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlRemoveSongLista, json=removeSongLista)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas AskAdminToBeArtist

setUserNormal = {
    'email': 'alvaro@gmail.es',
    'alias': 'alvaro',
    'contrasenya': '1234',
    'tipoUsuario': 'normalUser'
}

setUserArtista = {
    'email': 'mario@gmail.com',
    'alias': 'mario',
    'contrasenya': '1234',
    'tipoUsuario': 'artista'
}

askAdminToBeArtist = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
}

askAdminToBeArtistErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234'
}

askAdminToBeArtistErrorContrasenya = {
    'idUsr': 'usuario:3',
    'contrasenya': '12345'
}

askAdminToBeArtistErrorArtista = {
    'idUsr': 'usuario:4',
    'contrasenya': '1234'
}

askAdminToBeArtistErrorAdmin = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}


print("Pruebas askAdminToBeArtist")
print(requests.post(urlSetUser, json=setUserNormal).status_code)
print(requests.post(urlSetUser, json=setUserArtista).status_code)
print(requests.post(urlAskAdminToBeArtist, json=askAdminToBeArtist).status_code)
print(requests.post(urlAskAdminToBeArtist, json=askAdminToBeArtistErrorUsuario).status_code)
print(requests.post(urlAskAdminToBeArtist, json=askAdminToBeArtistErrorContrasenya).status_code)
print(requests.post(urlAskAdminToBeArtist, json=askAdminToBeArtistErrorArtista).status_code)
print(requests.post(urlAskAdminToBeArtist, json=askAdminToBeArtistErrorAdmin).status_code)


# Pruebas acceptArtist

acceptArtist = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:1'
}

acceptArtistErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:1'
}

acceptArtistErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idNotificacion': 'notificacion:1'
}

acceptArtistErrorNotificacion = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:10'
}

acceptArtistErrorUsuarioEmisor = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:2'
}

acceptArtistErrorTipo = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:3'
}

acceptArtistErrorAdmin = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:1'
}

notificacionErrorUsuarioEmisor = {
    'idUsuarioEmisor': 'usuario:6',
    'tipoNotificacion': 'quieroArtista'
}

notificacionErrorTipo = {
    'idUsuarioEmisor': 'usuario:1',
    'tipoNotificacion': 'quieroArtista2'
}



r.hmset('notificacion:2', notificacionErrorUsuarioEmisor)
r.hmset('notificacion:3', notificacionErrorTipo)

print("Pruebas acceptArtist")

print(requests.post(urlAcceptArtist, json=acceptArtistErrorUsuario).status_code)
print(requests.post(urlAcceptArtist, json=acceptArtistErrorContrasenya).status_code)
print(requests.post(urlAcceptArtist, json=acceptArtistErrorNotificacion).status_code)
print(requests.post(urlAcceptArtist, json=acceptArtistErrorUsuarioEmisor).status_code)
print(requests.post(urlAcceptArtist, json=acceptArtistErrorTipo).status_code)
print(requests.post(urlAcceptArtist, json=acceptArtistErrorAdmin).status_code)
print(requests.post(urlAcceptArtist, json=acceptArtist).status_code)

r.delete('notificacion:2')
r.delete('notificacion:3')

# Pruebas GetTotRepTime
GetTotRepTime = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

GetTotRepTimeErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234'
}

GetTotRepTimeErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345'
}

GetTotRepTimeErrorAdmin = {
    'idUsr': 'usuario:3',
    'contrasenya': '1234'
}

print("Pruebas GetTotRepTime")

respuesta = requests.post(urlGetTotRepTime, json=GetTotRepTime)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetTotRepTime, json=GetTotRepTimeErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetTotRepTime, json=GetTotRepTimeErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetTotRepTime, json=GetTotRepTimeErrorAdmin)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas AddSecondsToSong
AddSecondsToSong = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'segundos': 10
}

AddSecondsToSongErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'segundos': 10
}

AddSecondsToSongErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idAudio': 'audio:1',
    'segundos': 10
}

AddSecondsToSongErrorAudio = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:10',
    'segundos': 10
}

AddSecondsToSongErrorSeconds = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'segundos': -10
}

print("Pruebas AddSecondsToSong")
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSong).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorUsuario).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorContrasenya).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorAudio).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorSeconds).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSong).status_code)
respuesta = requests.post(urlGetTotRepTime, json=GetTotRepTime)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas SetFolder
SetFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreCarpeta': 'carpeta:1',
    'privacidadCarpeta': 'publica'
}

SetFolderErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'nombreCarpeta': 'carpeta:1',
    'privacidadCarpeta': 'publica'
}

SetFolderErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'nombreCarpeta': 'carpeta:1',
    'privacidadCarpeta': 'publica'
}

SetFolderErrorCarpeta = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'nombreCarpeta': 'carpeta:2',
    'privacidadCarpeta': 'publica',
}

SetFolderErrorPrivacidad = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreCarpeta': 'carpeta:1',
    'privacidadCarpeta': 'publica2'
}

print("Pruebas SetFolder")
print(requests.post(urlSetFolder, json=SetFolder).status_code)
print(requests.post(urlSetFolder, json=SetFolderErrorUsuario).status_code)
print(requests.post(urlSetFolder, json=SetFolderErrorContrasenya).status_code)
print(requests.post(urlSetFolder, json=SetFolderErrorCarpeta).status_code)
print(requests.post(urlSetFolder, json=SetFolderErrorPrivacidad).status_code)

# Pruebas AddListToFolder
AddListToFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:1'
}

AddListToFolderErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:1'
}

AddListToFolderErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:1'
}

AddListToFolderErrorCarpeta = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:10',
    'idLista': 'lista:1'
}

AddListToFolderErrorLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:10'
}

AddListToFolderErrorNoInUser = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:2',
    'idLista': 'lista:2'
}

AddListToFolderListPrivate = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:4'
}

print("Pruebas AddListToFolder")
print(requests.post(urlAddListToFolder, json=AddListToFolder).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorUsuario).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorContrasenya).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorCarpeta).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorLista).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorNoInUser).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderListPrivate).status_code)