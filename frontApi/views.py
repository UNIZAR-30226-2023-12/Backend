from django.shortcuts import render
from django.http import JsonResponse
import json
import redis
from DAOS import daoAudio
from DAOS import daoUsuario
from DAOS import daoGlobal

from Audios import moduloAudios

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
    id = request.GET.get('idSong')
    print("id: ", id)
    calidadAlta = request.GET.get('calidadAlta')
    print("calidadAlta: ", calidadAlta)

    fichero = ""
    if calidadAlta == "True":
        fichero = daoAudio.obtenerFicheroAltaCalidad(r, id)
    else:
        fichero = daoAudio.obtenerFicheroBajaCalidad(r, id)

    # Gets the serialized audio
    return JsonResponse({'fichero': fichero})

# View para añadir una canción a la base de datos
@csrf_exempt
def SetSong(request):

    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        moduloAudios.anyadirCancion(r, json_data)
        
        return True
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def SetUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        # Stores the user in the database
        daoUsuario.setUsuario(r, json_data)
        
        return True
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        

def ValidateUser(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        # json_data = json.loads(request.body)

        # Validates the user
        #data = json.loads(request.data)

        #print(data)
        
        if request.POST.get('contrasenya') == daoUsuario.getContrasenya(r, request.POST.get('id')):
            return JsonResponse({'validate': True})
        else:
            return JsonResponse({'validate': False})

    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        