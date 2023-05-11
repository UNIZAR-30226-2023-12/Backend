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
urlRemoveListFromFolder = 'http://127.0.0.1:8081/RemoveListFromFolder/'
urlRemoveFolder = 'http://127.0.0.1:8081/RemoveFolder/'
urlGetFolder = 'http://127.0.0.1:8081/GetFolder/'
urlGetFoldersUsr = 'http://127.0.0.1:8081/GetFoldersUsr/'
urlGetListasFolder = 'http://127.0.0.1:8081/GetListasFolder/'
urlAskFriend = 'http://127.0.0.1:8081/AskFriend/'
urlAcceptFriend = 'http://127.0.0.1:8081/AcceptFriend/'
urlGetFriends = 'http://127.0.0.1:8081/GetFriends/'
urlRemoveFriend = 'http://127.0.0.1:8081/RemoveFriend/'
urlSubscribeToArtist = 'http://127.0.0.1:8081/SubscribeToArtist/'
urlUnsubscribeToArtist = 'http://127.0.0.1:8081/UnsubscribeToArtist/'
urlGetNotificationsUsr = 'http://127.0.0.1:8081/GetNotificationsUsr/'
urlGetNotification = 'http://127.0.0.1:8081/GetNotification/'
urlRemoveNotification = 'http://127.0.0.1:8081/RemoveNotification/'
urlSetLastSecondHeared = 'http://127.0.0.1:8081/SetLastSecondHeared/'
urlGetLastSecondHeared = 'http://127.0.0.1:8081/GetLastSecondHeared/'


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
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:1' 
}

getUserErroneo = {
    'idUsr': 'usuario:4',
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:4'
}

getUserContrasenyaErronea = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idUsrGet' : 'usuario:1'
}

getUserOtroUser = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:2'
}



print("Pruebas get user")
respuesta = requests.post(urlGetUser, json=getUser)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetUser, json=getUserErroneo)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetUser, json=getUserContrasenyaErronea)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetUser, json=getUserOtroUser)
print(str(respuesta.status_code) + " " + str(respuesta.json()))



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
    'contrasenya': '1234',
    'idUsrGet': 'usuario:1'
}

getListasUsrErrorUsuario = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrGet': 'usuario:3'
}

getListasUsrErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idUsrGet': 'usuario:1'
}

getListasUsrPublicas = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrGet': 'usuario:2'
}

getListasUsrPublicas2 = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idUsrGet': 'usuario:1'
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

# Pruebas AddSecondsToSong
AddSecondsToSong = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'second': 10
}

AddSecondsToSongErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'second': 10
}

AddSecondsToSongErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idAudio': 'audio:1',
    'second': 10
}

AddSecondsToSongErrorAudio = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:10',
    'second': 10
}

AddSecondsToSongErrorSeconds = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'second': -10
}

AddSecondsToSong2 = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'audio:2',
    'second': 10
}

GetTotRepTime = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

print("Pruebas AddSecondsToSong")
respuesta = requests.post(urlGetTotRepTime, json=GetTotRepTime)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSong2).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSong).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorUsuario).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorContrasenya).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorAudio).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSongErrorSeconds).status_code)
print(requests.post(urlAddSecondsToSong, json=AddSecondsToSong).status_code)

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
exit(0)


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
    'idLista': 'lista:3'
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

AddListToFolderPublicList = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:2',
    'idLista': 'lista:3'
}

print("Pruebas AddListToFolder")
print(requests.post(urlAddListToFolder, json=AddListToFolder).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderPublicList).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorUsuario).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorContrasenya).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorCarpeta).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorLista).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderErrorNoInUser).status_code)
print(requests.post(urlAddListToFolder, json=AddListToFolderListPrivate).status_code)

# Pruebas GetListasFolder
GetListasFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1'
}

print("Pruebas GetListasFolder")
respuesta = requests.post(urlGetListasFolder, json=GetListasFolder)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas RemoveListFromFolder

RemoveListFromFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:3'
}

RemoveListFromFolderErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:1'
}

RemoveListFromFolderErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:1'
}

RemoveListFromFolderErrorCarpeta = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:10',
    'idLista': 'lista:1'
}

RemoveListFromFolderErrorLista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:10'
}

RemoveListFromFolderErrorNoInUser = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:2',
    'idLista': 'lista:3'
}

RemoveListFromFolderListNotInFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1',
    'idLista': 'lista:4'
}

print("Pruebas RemoveListFromFolder")
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolderErrorUsuario).status_code)
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolderErrorContrasenya).status_code)
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolderErrorCarpeta).status_code)
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolderErrorLista).status_code)
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolderErrorNoInUser).status_code)
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolderListNotInFolder).status_code)
print(requests.post(urlRemoveListFromFolder, json=RemoveListFromFolder).status_code)

# Pruebas RemoveFolder

RemoveFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1'
}

RemoveFolder2 = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:2'
}

RemoveFolderErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:1'
}

RemoveFolderErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idCarpeta': 'carpeta:1'
}

RemoveFolderErrorCarpeta = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:10'
}

RemoveFolderErrorForbidden = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:2'
}

print("Pruebas RemoveFolder")
print(requests.post(urlRemoveFolder, json=RemoveFolderErrorUsuario).status_code)
print(requests.post(urlRemoveFolder, json=RemoveFolderErrorContrasenya).status_code)
print(requests.post(urlRemoveFolder, json=RemoveFolderErrorCarpeta).status_code)
print(requests.post(urlRemoveFolder, json=RemoveFolderErrorForbidden).status_code)
print(requests.post(urlRemoveFolder, json=RemoveFolder).status_code)
print(requests.post(urlRemoveFolder, json=RemoveFolder2).status_code)

# Pruebas GetFolder

GetFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:3'
}

GetFolderErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:3'
}

GetFolderErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idCarpeta': 'carpeta:3'
}

GetFolderErrorCarpeta = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:10'
}

GetFolderErrorForbidden = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:4'
}

GetFolder2 = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idCarpeta': 'carpeta:3'
}

SetFolder = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'nombreCarpeta': 'Carpeta X',
    'privacidadCarpeta': 'publica'
}

SetFolder2 = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'nombreCarpeta': 'Carpeta Y',
    'privacidadCarpeta': 'privada'
}

print("Pruebas GetFolder")

print(requests.post(urlSetFolder, json=SetFolder).status_code)
print(requests.post(urlSetFolder, json=SetFolder2).status_code)
respuesta = requests.post(urlGetFolder, json=GetFolder)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFolder, json=GetFolderErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFolder, json=GetFolderErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFolder, json=GetFolderErrorCarpeta)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFolder, json=GetFolderErrorForbidden)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFolder, json=GetFolder2)
print(str(respuesta.status_code) + " " + str(respuesta.text))

# Pruebas GetFoldersUsr

GetFoldersUsr = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:1'
}

GetFoldersUsrErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:10'
}

GetFoldersUsrErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idUsrGet' : 'usuario:1'
}

GetFoldersUsrPublica = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:1'
}

GetFoldersUsrPublica2 = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrGet' : 'usuario:2'
}

print("Pruebas GetFoldersUsr")

respuesta = requests.post(urlGetFoldersUsr, json=GetFoldersUsr)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFoldersUsr, json=GetFoldersUsrErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFoldersUsr, json=GetFoldersUsrErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFoldersUsr, json=GetFoldersUsrPublica)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFoldersUsr, json=GetFoldersUsrPublica2)
print(str(respuesta.status_code) + " " + str(respuesta.text))

# Pruebas AskFriend

AskFriend = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAmigo': 'usuario:2'
}

AskFriendErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idAmigo': 'usuario:2'
}

AskFriendErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idAmigo': 'usuario:2'
}

AskFriendErrorAmigo = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAmigo': 'usuario:10'
}

AskFriendAlready = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAmigo': 'usuario:2'
}

print("Pruebas AskFriend")

print(requests.post(urlAskFriend, json=AskFriend).status_code)
print(requests.post(urlAskFriend, json=AskFriendErrorUsuario).status_code)
print(requests.post(urlAskFriend, json=AskFriendErrorContrasenya).status_code)
print(requests.post(urlAskFriend, json=AskFriendErrorAmigo).status_code)
r.sadd("amigos:usuario:1", "usuario:2")
r.sadd("amigos:usuario:2", "usuario:1")
print(requests.post(urlAskFriend, json=AskFriendAlready).status_code)
r.srem("amigos:usuario:1", "usuario:2")
r.srem("amigos:usuario:2", "usuario:1")

# Pruebas acceptFriend

AcceptFriend = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:2'
}

AcceptFriendErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:2'
}

AcceptFriendErrorContrasenya = {
    'idUsr': 'usuario:2',
    'contrasenya': '12345',
    'idNotificacion': 'notificacion:2'
}

AcceptFriendErrorNotificacion = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234',
    'idNotificacion': 'notificacion:10'
}

print("Pruebas acceptFriend")

print(requests.post(urlAcceptFriend, json=AcceptFriendErrorUsuario).status_code)
print(requests.post(urlAcceptFriend, json=AcceptFriendErrorContrasenya).status_code)
print(requests.post(urlAcceptFriend, json=AcceptFriendErrorNotificacion).status_code)
print(requests.post(urlAcceptFriend, json=AcceptFriend).status_code)

# Pruebas GetFriends

GetFriends = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

GetFriendsErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234'
}

GetFriendsErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345'
}

print("Pruebas GetFriends")
respuesta = requests.post(urlGetFriends, json=GetFriends)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFriends, json=GetFriendsErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.text))
respuesta = requests.post(urlGetFriends, json=GetFriendsErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.text))

# Prueba RemoveFriend

RemoveFriend = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAmigo': 'usuario:2'
}

RemoveFriendErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idAmigo': 'usuario:2'
}

RemoveFriendErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idAmigo': 'usuario:2'
}

RemoveFriendErrorAmigo = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAmigo': 'usuario:10'
}

RemoveFriendNotFriend = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAmigo': 'usuario:3'
}

print("Pruebas RemoveFriend")

print(requests.post(urlRemoveFriend, json=RemoveFriendErrorUsuario).status_code)
print(requests.post(urlRemoveFriend, json=RemoveFriendErrorContrasenya).status_code)
print(requests.post(urlRemoveFriend, json=RemoveFriendErrorAmigo).status_code)
print(requests.post(urlRemoveFriend, json=RemoveFriendNotFriend).status_code)
print(requests.post(urlRemoveFriend, json=RemoveFriend).status_code)

# Pruebas SubscribeToArtist

SubscribeToArtist = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:3'
}

SubscribeToArtistErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:3'
}

SubscribeToArtistErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idUsrArtista': 'usuario:3'
}

SubscribeToArtistErrorArtista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:10'
}

SubscribeToArtistNotArtist = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:2'
}

SubscribeToArtistAlready = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:3'
}

print("Pruebas SubscribeToArtist")

print(requests.post(urlSubscribeToArtist, json=SubscribeToArtistErrorUsuario).status_code)
print(requests.post(urlSubscribeToArtist, json=SubscribeToArtistErrorContrasenya).status_code)
print(requests.post(urlSubscribeToArtist, json=SubscribeToArtistErrorArtista).status_code)
print(requests.post(urlSubscribeToArtist, json=SubscribeToArtistNotArtist).status_code)
print(requests.post(urlSubscribeToArtist, json=SubscribeToArtist).status_code)
print(requests.post(urlSubscribeToArtist, json=SubscribeToArtistAlready).status_code)

# Pruebas UnsubscribeToArtist

UnsubscribeToArtist = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:3'
}

UnsubscribeToArtistErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:3'
}

UnsubscribeToArtistErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345',
    'idUsrArtista': 'usuario:3'
}

UnsubscribeToArtistErrorArtista = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:10'
}

UnsubscribeToArtistNotSubscribed = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idUsrArtista': 'usuario:3'
}


print("Pruebas UnsubscribeToArtist")

print(requests.post(urlUnsubscribeToArtist, json=UnsubscribeToArtistErrorUsuario).status_code)
print(requests.post(urlUnsubscribeToArtist, json=UnsubscribeToArtistErrorContrasenya).status_code)
print(requests.post(urlUnsubscribeToArtist, json=UnsubscribeToArtistErrorArtista).status_code)
print(requests.post(urlUnsubscribeToArtist, json=UnsubscribeToArtist).status_code)
print(requests.post(urlUnsubscribeToArtist, json=UnsubscribeToArtistNotSubscribed).status_code)

# Pruebas GetNotificationsUsr

GetNotificationsUsr = {
    'idUsr': 'usuario:2',
    'contrasenya': '1234'
}

GetNotificationsUsrErrorUsuario = {
    'idUsr': 'usuario:10',
    'contrasenya': '1234'
}

GetNotificationsUsrErrorContrasenya = {
    'idUsr': 'usuario:1',
    'contrasenya': '12345'
}

print("Pruebas GetNotificationsUsr")
print(requests.post(urlAskFriend, json=AskFriend).status_code)

respuesta = requests.post(urlGetNotificationsUsr, json=GetNotificationsUsr)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetNotificationsUsr, json=GetNotificationsUsrErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetNotificationsUsr, json=GetNotificationsUsrErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas GetNotification

GetNotification = {
    'idUsr' : 'usuario:2',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '1234'
}

GetNotificationErrorUsuario = {
    'idUsr' : 'usuario:10',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '1234'
}

GetNotificationErrorContrasenya = {
    'idUsr' : 'usuario:2',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '12345'
}

GetNotificationErrorNotificacion = {
    'idUsr' : 'usuario:2',
    'idNotificacion': 'notificacion:10',
    'contrasenya': '1234'
}

GetNotificationForbbiden = {
    'idUsr' : 'usuario:1',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '1234'
}

print("Pruebas GetNotification")

respuesta = requests.post(urlGetNotification, json=GetNotification)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetNotification, json=GetNotificationErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetNotification, json=GetNotificationErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetNotification, json=GetNotificationErrorNotificacion)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetNotification, json=GetNotificationForbbiden)
print(str(respuesta.status_code) + " " + str(respuesta.json()))

# Pruebas RemoveNotification

RemoveNotification = {
    'idUsr' : 'usuario:2',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '1234'
}

RemoveNotificationErrorUsuario = {
    'idUsr' : 'usuario:10',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '1234'
}

RemoveNotificationErrorContrasenya = {
    'idUsr' : 'usuario:2',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '12345'
}

RemoveNotificationErrorNotificacion = {
    'idUsr' : 'usuario:2',
    'idNotificacion': 'notificacion:10',
    'contrasenya': '1234'
}

RemoveNotificationForbbiden = {
    'idUsr' : 'usuario:1',
    'idNotificacion': 'notificacion:3',
    'contrasenya': '1234'
}

print("Pruebas RemoveNotification")

print(requests.post(urlRemoveNotification, json=RemoveNotificationErrorUsuario).status_code)
print(requests.post(urlRemoveNotification, json=RemoveNotificationErrorContrasenya).status_code)
print(requests.post(urlRemoveNotification, json=RemoveNotificationErrorNotificacion).status_code)
print(requests.post(urlRemoveNotification, json=RemoveNotificationForbbiden).status_code)
print(requests.post(urlRemoveNotification, json=RemoveNotification).status_code)

# Pruebas SetLastSecondHeared

SetLastSecondHeared = {
    'idUsr' : 'usuario:2',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'second': 10
}

SetLastSecondHearedErrorUsuario = {
    'idUsr' : 'usuario:10',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'second': 10
}

SetLastSecondHearedErrorContrasenya = {
    'idUsr' : 'usuario:2',
    'contrasenya': '12345',
    'idAudio': 'audio:1',
    'second': 10
}

SetLastSecondHearedErrorAudio = {
    'idUsr' : 'usuario:2',
    'contrasenya': '1234',
    'idAudio': 'audio:10',
    'second': 10
}

SetLastSecondHearedErrorSegundo = {
    'idUsr' : 'usuario:2',
    'contrasenya': '1234',
    'idAudio': 'audio:1',
    'second': -1
}

print("Pruebas SetLastSecondHeared")

print(requests.post(urlSetLastSecondHeared, json=SetLastSecondHearedErrorUsuario).status_code)
print(requests.post(urlSetLastSecondHeared, json=SetLastSecondHearedErrorContrasenya).status_code)
print(requests.post(urlSetLastSecondHeared, json=SetLastSecondHearedErrorAudio).status_code)
print(requests.post(urlSetLastSecondHeared, json=SetLastSecondHearedErrorSegundo).status_code)
print(requests.post(urlSetLastSecondHeared, json=SetLastSecondHeared).status_code)

# Pruebas GetLastSecondHeared

GetLastSecondHeared = {
    'idUsr' : 'usuario:2',
    'contrasenya': '1234',
    'idAudio': 'audio:1'
}

GetLastSecondHearedErrorUsuario = {
    'idUsr' : 'usuario:10',
    'contrasenya': '1234',
    'idAudio': 'audio:1'
}

GetLastSecondHearedErrorContrasenya = {
    'idUsr' : 'usuario:2',
    'contrasenya': '12345',
    'idAudio': 'audio:1'
}

GetLastSecondHearedErrorAudio = {
    'idUsr' : 'usuario:2',
    'contrasenya': '1234',
    'idAudio': 'audio:10'
}

print("Pruebas GetLastSecondHeared")

respuesta = requests.post(urlGetLastSecondHeared, json=GetLastSecondHeared)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLastSecondHeared, json=GetLastSecondHearedErrorUsuario)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLastSecondHeared, json=GetLastSecondHearedErrorContrasenya)
print(str(respuesta.status_code) + " " + str(respuesta.json()))
respuesta = requests.post(urlGetLastSecondHeared, json=GetLastSecondHearedErrorAudio)
print(str(respuesta.status_code) + " " + str(respuesta.json()))