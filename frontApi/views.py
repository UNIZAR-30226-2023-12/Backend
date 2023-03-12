from django.shortcuts import render
from django.http import JsonResponse
import json
import redis
from Audios import daoAudio
from Usuarios import daoUsuario
from Global import daoGlobal

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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
def GetSong(request):
    id = request.GET.get('idSong')
    calidadAlta = request.GET.get('calidadAlta')

    # Gets the serialized audio
    return daoAudio.obtenerFicheroAltaCalidad(r, id)

def SetSong(request):

    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        # Stores the song in the database
        daoAudio.guardarCancion(json_data)
        
        return True
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def SetUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        # Stores the user in the database
        daoUsuario.guardarUsuario(json_data)
        
        return True
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        

def ValidateUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        # json_data = json.loads(request.body)

        # Validates the user 
        return request.Get.get('contrasenya') == daoUsuario.obtenerContrasenya(r, request.Get.get('id'))
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        