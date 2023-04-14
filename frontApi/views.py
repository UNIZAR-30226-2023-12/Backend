from django.shortcuts import render
from django.http import JsonResponse
import json
import redis

from Configuracion import constantesPrefijosClaves as constantes
from Configuracion import constantesErroresHTTP as erroresHTTP

from Audios import moduloAudios
from Usuarios import usuarios

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

r = redis.Redis(host=settings.REDIS_SERVER_IP, port=settings.REDIS_SERVER_PORT, db=settings.REDIS_DATABASE, decode_responses=True)#, username=settings.REDIS_USER, password=settings.REDIS_PASSWORD)

# echo request
@csrf_exempt
def echo(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        return JsonResponse(json_data)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# Create your views here.
@csrf_exempt
def GetSong(request):
    fichero = -1
    # Compruebo que el método sea GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    id = request.GET.get('idSong')
    calidadAlta = request.GET.get('calidadAlta')
    esCancion = request.GET.get('esCancion')

    if esCancion == "True":
        if calidadAlta == "True":
            fichero = moduloAudios.obtenerFicheroCancion(r, id, 'alta')
        elif calidadAlta == "False":
            fichero = moduloAudios.obtenerFicheroCancion(r, id, 'baja')
    elif esCancion == "False":
        if calidadAlta == "True":
            fichero = moduloAudios.obtenerFicheroPodcast(r, id, 'alta')
        elif calidadAlta == "False":
            fichero = moduloAudios.obtenerFicheroPodcast(r, id, 'baja')

    if fichero == 419 or fichero == 424 or fichero == 430 or fichero == 425:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=fichero)
    else:
        # Gets the serialized audio
        return JsonResponse({'fichero': fichero})
    
# View que devuelve una lista de canciones
@csrf_exempt
def GetSongs(request):
    # Compruebo que el método sea GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    listaIDs = request.GET.get('listaIDs')
    calidadAlta = request.GET.get('calidadAlta')
    esCancion = request.GET.get('esCancion')

    if esCancion == "True":
        if calidadAlta == "True":
            ficheros = moduloAudios.obtenerFicheroCanciones(r, listaIDs, 'alta')
        elif calidadAlta == "False":
            ficheros = moduloAudios.obtenerFicheroCanciones(r, listaIDs, 'baja')
    elif esCancion == "False":
        if calidadAlta == "True":
            ficheros = moduloAudios.obtenerFicheroPodcasts(r, listaIDs, 'alta')
        elif calidadAlta == "False":
            ficheros = moduloAudios.obtenerFicheroPodcasts(r, listaIDs, 'baja')
    
    if ficheros == 419 or ficheros == 424 or ficheros == 430 or ficheros == 425:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=ficheros)
    else:
        # Gets the serialized audio
        return JsonResponse({'ficheros': ficheros})

# View para añadir una canción a la base de datos
@csrf_exempt
def SetSong(request):
    # Compruebo que el método sea POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    status = usuarios.ValidateUser(r, idUsuario, contrasenya)

    if status == erroresHTTP.OK:

        # Añado la canción a la base de datos
        status = moduloAudios.anyadirCancion(r, json_data)

        if status != 0:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=status)

        return JsonResponse({'msg': 'Cancion añadida correctamente'}, status=erroresHTTP.OK)
    else:
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=status)

@csrf_exempt
def SetUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        # Stores the user in the database
        status = usuarios.setUser(r, json_data)
        if(status == erroresHTTP.OK):
            diccionarioLista = {constantes.CLAVE_NOMBRE_LISTA : "Favoritos", 
                                constantes.CLAVE_PRIVACIDAD_LISTA : constantes.LISTA_PRIVADA, 
                                constantes.CLAVE_TIPO_LISTA : constantes.LISTA_TIPO_FAVORITOS}
            usuarios.setLista(r, diccionarioLista)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
@csrf_exempt
def ValidateUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

        # Validates the user
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)

        return JsonResponse({'status': status}, status=status)

    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
def SetLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

        # Validates the user
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)
        # Creamos el diccionario lista y quitamos los campos que no son necesarios
        diccionarioLista = json_data.copy()
        del diccionarioLista[constantes.CLAVE_ID_USUARIO]
        del diccionarioLista[constantes.CLAVE_CONTRASENYA]
        status = usuarios.setLista(r, diccionarioLista)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
def ChangeNameListRepUsr(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)

        # Si no es valido devuelvo el error
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)
        
        
        idLista = json_data[constantes.CLAVE_ID_LISTA]
        nombre = json_data[constantes.CLAVE_NOMBRE_LISTA]
        # Stores the user in the database
        status = usuarios.setNombreLista(r, idLista, nombre)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def SetSongLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)
        # Si no es valido devuelvo el error
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)
        
        idAudio = json_data[constantes.CLAVE_ID_AUDIO]
        if (moduloAudios.existeCancion(r, idAudio) == False):
            return JsonResponse({'error': 'No existe el audio'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
        
        idLista = json_data[constantes.CLAVE_ID_LISTA]
        # Stores the user in the database
        status = usuarios.setSongLista(r, idLista, idAudio)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt 
def GetListaRepUsr(request):
    if request.method == 'GET':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)
        # Si no es valido devuelvo el error
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)

        # Stores the user in the database
        lista = usuarios.getListasUsr(r, idUsuario)
        
        return JsonResponse({constantes.CLAVE_LISTAS: lista}, status=erroresHTTP.OK)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def RemoveSongLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)
        # Si no es valido devuelvo el error
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)
        
        idAudio = json_data[constantes.CLAVE_ID_AUDIO]
        idLista = json_data[constantes.CLAVE_ID_LISTA]
        # Stores the user in the database
        status = usuarios.removeSongLista(r, idLista, idAudio)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
# View para solicitar al administrador que un usuario sea artista
@csrf_exempt    
def AskAdminToBeArtist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    
    # Primero valido que el usuario que me están pasando sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.AskAdminToBeArtist(r, idUsuario)

    return JsonResponse({'status': status}, status=status)

# View para aceptar a un usuario como artista
@csrf_exempt
def AcceptArtist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario and idNotificacion
    json_data = json.loads(request.body)
    
    # Primero valido que el usuario que me están pasando sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    status = usuarios.AcceptArtist(r, idUsuario, idNotificacion)

    return JsonResponse({'status': status}, status=status)

@csrf_exempt
def ValidateUserEmail(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    email = json_data[constantes.CLAVE_EMAIL]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    respuesta = usuarios.validateUserEmail(r, email, contrasenya)

    return JsonResponse({constantes.CLAVE_ID_USUARIO: respuesta[constantes.CLAVE_ID_USUARIO]}, status=respuesta["status"])

