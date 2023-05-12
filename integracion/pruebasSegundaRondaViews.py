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

urlRemoveUser = 'http://127.0.0.1:8081/RemoveUser/'
urlRejectFriend = 'http://127.0.0.1:8081/RejectFriend/'
urlRejectArtista = 'http://127.0.0.1:8081/RejectArtista/'
urlSetPrivacidadCarpeta = 'http://127.0.0.1:8081/SetPrivacidadCarpeta/'
urlGetPrivacidadCarpeta = 'http://127.0.0.1:8081/GetPrivacidadCarpeta/'
urlGetSubscriptionsUsr = 'http://127.0.0.1:8081/GetSubscriptionsUsr/'
urlIsSubscribedToArtist = 'http://127.0.0.1:8081/IsSubscribedToArtist/'
urlGetImagenUsr = 'http://127.0.0.1:8081/GetImagenPerfilUsr/'

setUser = {
    'email': 'alvaro@gmail.com',
    'contrasenya': '1234',
    'alias': 'usuario1',
    'tipoUsuario': 'admin'
}

setUser2 = {
    'email': 'hugo@gmail.com',
    'contrasenya': '1234',
    'alias': 'usuario2',
    'tipoUsuario': 'admin'
}

setUser3 = {
    'email': 'mario@gmail.com',
    'contrasenya': '1234',
    'alias': 'usuario3',
    'tipoUsuario': 'normalUser'
}

setUser4 = {
    'email': 'cristina@gmail.com',
    'contrasenya': '1234',
    'alias': 'usuario4',
    'tipoUsuario': 'artista'
}



# Creamos cuatro usuarios y subscribimos al usuario 1 al usuario 4
requests.post(urlFlushDB)
requests.post(urlSetUser, json=setUser)
requests.post(urlSetUser, json=setUser2)
requests.post(urlSetUser, json=setUser3)
requests.post(urlSetUser, json=setUser4)


# Pruebas GetSubscriptionsUsr
print('Pruebas GetSubscriptionsUsr')
print(requests.post(urlSubscribeToArtist, json={'idUsr' : 'usuario:1', 'contrasenya' : '1234','idUsrArtista' : 'usuario:4'}).status_code)
respuesta = requests.post(urlGetSubscriptionsUsr, json={'idUsr': 'usuario:1', 'contrasenya': '1234'})
print(str(respuesta.status_code) + ' ' + str(respuesta.json()))

# Pruebas isSubscribedToArtist
print('Pruebas isSubscribedToArtist')
respuesta = requests.post(urlIsSubscribedToArtist, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idUsrArtista' : 'usuario:4'})
print(str(respuesta.status_code) + ' ' + str(respuesta.json()))

# Eliminamos el usuario 4, el usuario1 no se desubscribe hasta que un get del usuario artista da error
print('Pruebas Getuser')
respuesta = requests.post(urlGetUser, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idUsrGet' : 'usuario:4'})
print(str(respuesta.status_code) + ' ' + str(respuesta.json()))
print(requests.post(urlRemoveUser, json={'idUsr': 'usuario:4', 'contrasenya': '1234', 'idUsrEliminar' : 'usuario:4'}).status_code)
respuesta = requests.post(urlGetUser, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idUsrGet' : 'usuario:4'})
print(str(respuesta.status_code) + ' ' + str(respuesta.json()))

# Pruebas RejectFriend
print('Pruebas RejectFriend')
print(requests.post(urlAskFriend, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idAmigo' : 'usuario:2'}).status_code)
print(requests.post(urlRejectFriend, json={'idUsr': 'usuario:2', 'contrasenya': '1234', 'idNotificacion' : 'notificacion:1'}).status_code)

# Pruebas RejectArtista
print('Pruebas RejectArtista')
print(requests.post(urlAskAdminToBeArtist, json={'idUsr': 'usuario:3', 'contrasenya': '1234'}).status_code)
print(requests.post(urlRejectArtista, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idNotificacion' : 'notificacion:2'}).status_code)

# Pruebas setPrivacidadCarpeta
print('Pruebas setPrivacidadCarpeta')
print(requests.post(urlSetFolder, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'nombreCarpeta' : 'carpeta1', 'privacidadCarpeta' : 'publica'}).status_code)
print(requests.post(urlSetPrivacidadCarpeta, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idCarpeta' : 'carpeta:1', 'privacidadCarpeta' : 'privada'}).status_code)

# Pruebas getPrivacidadCarpeta
print('Pruebas getPrivacidadCarpeta')
respuesta = requests.post(urlGetPrivacidadCarpeta, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idCarpeta' : 'carpeta:1'})
print(str(respuesta.status_code) + ' ' + str(respuesta.json()))

# Pruebas GetImagenUsr
print('Pruebas GetImagenUsr')
respuesta = requests.post(urlGetImagenUsr, json={'idUsr': 'usuario:1', 'contrasenya': '1234', 'idUsr2' : 'usuario:1'})
print(str(respuesta.status_code) + ' ' + str(respuesta.json()))

