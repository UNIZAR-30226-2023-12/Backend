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

r = redis.Redis(host=settings.REDIS_SERVER_IP, port=settings.REDIS_SERVER_PORT, db=settings.REDIS_DATABASE, decode_responses=True, username=settings.REDIS_USER, password=settings.REDIS_PASSWORD)

# echo request
def echo(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        return json_data
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# Create your views here.
@csrf_exempt
def GetSong(request):
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

# View para añadir una canción a la base de datos
@csrf_exempt
def SetSong(request):
    # Compruebo que el método sea POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    contrasenya = request.POST.get('passwd')
    usuario = request.POST.get('usr')
    # Compruebo que el usuario sea válido
    status = usuarios.ValidateUser(r, usuario, contrasenya)
    if status == erroresHTTP.OK:
        # Parseo el JSON de la petición
        json_data = json.loads(request.body)

        # Añado la canción a la base de datos
        status = moduloAudios.anyadirCancion(r, json_data)
        if status != 0:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=status)

        return JsonResponse({'msg' 'Cancion añadida correctamente'}, status=200)
    else:
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=status)
   
def SetUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        
        
        # Stores the user in the database
        status = usuarios.setUser(r, json_data)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        

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
    
def SetLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        # Compruebo que el usuario sea válido
        respuesta = ValidateUser(r, request)
        # Si no es valido devuelvo el error
        if (respuesta != erroresHTTP.OK):
            return respuesta
        # Stores the list in the database
        status = usuarios.setLista(r, json_data)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def ChangeNameListRepUsr(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        respuesta = ValidateUser(r, request)
        # Si no es valido devuelvo el error
        if (respuesta != erroresHTTP.OK):
            return respuesta
        
        idLista = json_data[constantes.CLAVE_ID_LISTA]
        nombre = json_data[constantes.CLAVE_NOMBRE_LISTA]
        # Stores the user in the database
        status = usuarios.setNombreLista(r, idLista, nombre)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def SetSongLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        respuesta = ValidateUser(r, request)
        # Si no es valido devuelvo el error
        if (respuesta != erroresHTTP.OK):
            return respuesta
        
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
    
def GetListaRepUsr(request):
    if request.method == 'GET':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        respuesta = ValidateUser(r, request)
        # Si no es valido devuelvo el error
        if (respuesta != erroresHTTP.OK):
            return respuesta
        
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]

        # Stores the user in the database
        lista = usuarios.getListasUsr(r, idUsuario)
        
        return JsonResponse({constantes.CLAVE_LISTAS: lista}, status=erroresHTTP.OK)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def RemoveSongLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Compruebo que el usuario sea válido
        respuesta = ValidateUser(r, request)
        # Si no es valido devuelvo el error
        if (respuesta.status_code != erroresHTTP.OK):
            return respuesta
        
        idAudio = json_data[constantes.CLAVE_ID_AUDIO]
        idLista = json_data[constantes.CLAVE_ID_LISTA]
        # Stores the user in the database
        status = usuarios.removeSongLista(r, idLista, idAudio)
        
        return JsonResponse({'status': status}, status=status)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

    

        
        