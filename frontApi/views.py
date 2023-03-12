from django.shortcuts import render
from django.http import JsonResponse
import json
from Audios import daoAudio
from Usuarios import daoUsuario
from Global import daoGlobal

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
    return daoAudio.getCancion(id, calidadAlta)

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