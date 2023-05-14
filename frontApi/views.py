from django.shortcuts import render
from django.http import JsonResponse
import json
import redis

from Configuracion import constantesPrefijosClaves as constantes
from Configuracion import constantesErroresHTTP as erroresHTTP

from Audios import moduloAudios
from Usuarios import usuarios

from recomendador import generacion_datos as gen_datos
#from recomendador import recomendador as rec

from Global import ModuloGlobal

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random

r = redis.Redis(host=settings.REDIS_SERVER_IP, port=settings.REDIS_SERVER_PORT, db=settings.REDIS_DATABASE, decode_responses=True, username=settings.REDIS_USER, password=settings.REDIS_PASSWORD)

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
    # Compruebo que el método sea POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    jsonData = json.loads(request.body)
    idAudio = jsonData[constantes.CLAVE_ID_AUDIO]
    idUsuario = jsonData[constantes.CLAVE_ID_USUARIO]
    contrasenya = jsonData[constantes.CLAVE_CONTRASENYA]


    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    audio = moduloAudios.obtenerDiccionarioCancion(r, idAudio)
    del audio[constantes.CLAVE_FICHERO_ALTA_CALIDAD]
    del audio[constantes.CLAVE_FICHERO_BAJA_CALIDAD]

    gen_datos.add_audio_prediction_temporal(r, idUsuario, idAudio)

    return JsonResponse({constantes.CLAVE_ID_AUDIO: audio}, status=erroresHTTP.OK)
    
@csrf_exempt
def GetFicheroSong(request):
    fichero = -1
    # Compruebo que el método sea GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    id = request.GET.get(constantes.CLAVE_ID_AUDIO)
    calidadAlta = request.GET.get(constantes.CLAVE_CALIDAD_AUDIO)
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
        idUsr = request.GET.get('idUsr')
        if idUsr == None:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
        
        gen_datos.add_audio_prediction_temporal(r, idUsr, id)
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
    json_data['artista'] = idUsuario

    # Control de errores
    if (usuarios.getTipoUsr(r, idUsuario) == constantes.USUARIO_ARTISTA):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ARTISTA}, status=erroresHTTP.ERROR_USUARIO_NO_ARTISTA)

    if status == True:

        # Añado la canción a la base de datos
        status = moduloAudios.anyadirCancion(r, json_data)
        

        if status != 0:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=status)

        return JsonResponse({'msg': 'Cancion añadida correctamente'}, status=erroresHTTP.OK)
    else:
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)

@csrf_exempt
def SetUser(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)
    
    email = json_data[constantes.CLAVE_EMAIL]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    alias = json_data[constantes.CLAVE_ALIAS]
    tipoUsuario = json_data[constantes.CLAVE_TIPO_USUARIO]

    diccionarioUsuario = {constantes.CLAVE_EMAIL : email,
                            constantes.CLAVE_CONTRASENYA : contrasenya,
                            constantes.CLAVE_ALIAS : alias,
                            constantes.CLAVE_TIPO_USUARIO : tipoUsuario}

    # Control de errores
    if(usuarios.existeUsuarioEmail(r, email)):
        return JsonResponse({'error': 'El email ya existe'}, status=erroresHTTP.ERROR_USUARIO_EMAIL_YA_EXISTE)
    
    if(usuarios.tipoUsuarioValido(json_data[constantes.CLAVE_TIPO_USUARIO]) == False):
        return JsonResponse({'error': 'El tipo de usuario no es valido'}, status=erroresHTTP.ERROR_USUARIO_TIPO_NO_VALIDO)
    
    # No error, so add the user
    idUsuario = usuarios.setUser(r, diccionarioUsuario)

    diccionarioLista = {constantes.CLAVE_NOMBRE_LISTA : "Favoritos", 
                        constantes.CLAVE_PRIVACIDAD_LISTA : constantes.LISTA_PRIVADA, 
                        constantes.CLAVE_TIPO_LISTA : constantes.LISTA_TIPO_FAVORITOS,
                        constantes.CLAVE_ID_USUARIO : idUsuario}
    usuarios.setLista(r, idUsuario, diccionarioLista)

    return JsonResponse({constantes.CLAVE_ID_USUARIO: idUsuario}, status=erroresHTTP.OK)

@csrf_exempt
def GetUser(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioGet = json_data[constantes.CLAVE_ID_USUARIO + "Get"]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False and contrasenya != None):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioGet) == False):
        if(usuarios.isSubscribedToArtist(r, idUsuario, idUsuarioGet)):
            usuarios.unsubscribeToArtist(r, idUsuario, idUsuarioGet)
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    if(idUsuario != idUsuarioGet):
        return JsonResponse(usuarios.getUserPublicData(r, idUsuarioGet), status=erroresHTTP.OK)
    return JsonResponse(usuarios.getUser(r, idUsuarioGet), status=erroresHTTP.OK)

@csrf_exempt
def ValidateUser(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    email = json_data[constantes.CLAVE_EMAIL]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuario = usuarios.getIdEmailId(r, email)

    if(usuarios.existeUsuarioEmail(r, email) == False):
        return JsonResponse({'error': 'El email no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)

    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    return JsonResponse({constantes.CLAVE_ID_USUARIO: idUsuario}, status=erroresHTTP.OK)

    
@csrf_exempt
def SetLista(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)
    
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    nombreLista = json_data[constantes.CLAVE_NOMBRE_LISTA]
    privacidadLista = json_data[constantes.CLAVE_PRIVACIDAD_LISTA]
    tipoLista = json_data[constantes.CLAVE_TIPO_LISTA]
    diccionarioLista = {constantes.CLAVE_ID_USUARIO : idUsuario,
                        constantes.CLAVE_NOMBRE_LISTA : nombreLista,
                        constantes.CLAVE_PRIVACIDAD_LISTA : privacidadLista,
                        constantes.CLAVE_TIPO_LISTA : tipoLista}


    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    # Validates the user
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if (usuarios.isListaPrivacidadValida(diccionarioLista[constantes.CLAVE_PRIVACIDAD_LISTA]) == False):
        return JsonResponse({'error': 'La privacidad no es valida'}, status=erroresHTTP.ERROR_LISTA_PRIVACIDAD_INCORRECTA)
    if (usuarios.tipoListaValido(diccionarioLista[constantes.CLAVE_TIPO_LISTA]) == False):
        return JsonResponse({'error': 'El tipo de lista no es valido'}, status=erroresHTTP.ERROR_LISTA_TIPO_INCORRECTO)

    idLista = usuarios.setLista(r, idUsuario, diccionarioLista)
    return JsonResponse({constantes.CLAVE_ID_LISTA: idLista}, status=erroresHTTP.OK)
    
    
@csrf_exempt
def SetLastSecondHeared(request):
    # String idUsr, String contrasenya, String idAudio, int second
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
        idAudio = json_data[constantes.CLAVE_ID_AUDIO]
        second = json_data[constantes.CLAVE_SECONDS]

        # Validates the user
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)
        
        status = moduloAudios.setLastSecondHeared(r, idUsuario, idAudio, second)
        return JsonResponse({'status': status}, status=status)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def GetTopReproducciones(request):

    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)

    n = int(json_data[constantes.CLAVE_N])
    esPodcast = json_data[constantes.CLAVE_ES_PODCAST] == "1"
 

    if esPodcast:
        audios  = list(moduloAudios.obtenerTodosLosPodcasts(r))
    else:
        audios = moduloAudios.obtenerTodasLasCanciones(r)
        print(audios)
        audios  = list(audios)


    reproducciones = []

    # Obtiene las reproducciones de cada audio
    for audio in audios:
        reproducciones.append(moduloAudios.getReproducciones(r, audio))

    # pair the elements of the two lists
    pairs = list(zip(audios, reproducciones))

    # sort the pairs based on the values in the second list (i.e. b)
    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    # extract the first element of each pair (i.e. the elements of a) into a new list
    audios_ordenados = [pair[0] for pair in sorted_pairs]

    return JsonResponse({'topAudios': audios_ordenados[0:n]}, status=200)

@csrf_exempt
def ChangeNameListRepUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)

    # Compruebo que el usuario sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]
    nombre = json_data[constantes.CLAVE_NOMBRE_LISTA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_LISTA_NO_ENCONTRADA}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if (usuarios.isListaFromUser(r, idUsuario, idLista) == False):
        return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)
    
    # No error, so change the name
    usuarios.setNombreListaRep(r, idLista, nombre)
    
    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def SetSongLista(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)

    # Compruebo que el usuario sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    
    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La cancion no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    if (usuarios.isListaFromUser(r, idUsuario, idLista) == False):
        return JsonResponse({'error': 'La lista no pertenece al usuario'}, status=erroresHTTP.FORBIDDEN)
    
    # No error, so add the song to the list
    usuarios.anyadirAudioLista(r, idLista, idAudio)
    
    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def GetLista(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_LISTA_NO_ENCONTRADA}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if (usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.isListaPublica(r, idLista) == False):
        return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)

    return JsonResponse({constantes.PREFIJO_ID_LISTA: usuarios.getLista(r, idLista)}, status=erroresHTTP.OK)


@csrf_exempt
def GetListasUsr(request):
    if request.method != 'POST':
         # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)

    # Compruebo que el usuario sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioGet = json_data[constantes.CLAVE_ID_USUARIO + "Get"]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioGet) == False):
        if(usuarios.isSubscribedToArtist(r, idUsuario, idUsuarioGet)):
            usuarios.unsubscribeToArtist(r, idUsuario, idUsuarioGet)
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    if (idUsuario != idUsuarioGet):
        return JsonResponse({constantes.CLAVE_LISTAS: usuarios.getListasUsrPublicas(r, idUsuario)}, status=erroresHTTP.OK)
    return JsonResponse({constantes.CLAVE_LISTAS: usuarios.getListasUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def RemoveListaRepUsr(request):
    if request.method != 'POST':
         # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)

    # Compruebo que el usuario sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_LISTA_NO_ENCONTRADA}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if (usuarios.isListaFromUser(r, idUsuario, idLista) == False):
        return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)
    if(usuarios.getTipoListaRep(r, idLista) == constantes.LISTA_TIPO_FAVORITOS):
        return JsonResponse({'status': erroresHTTP.ERROR_LISTA_ES_FAVORITOS}, status=erroresHTTP.ERROR_LISTA_ES_FAVORITOS)

    # No error, so remove the list
    usuarios.removeLista(r, idUsuario, idLista)
    
    
    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

       
@csrf_exempt 
def GetAudiosLista(request):
    if request.method != 'POST':
         # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    # Parse the JSON data from the request body
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_LISTA_NO_ENCONTRADA}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.isListaPublica(r, idLista) == False):
        return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)

    return JsonResponse({constantes.CLAVE_PREFIJO_AUDIO: usuarios.getAudiosLista(r, idLista)}, status=erroresHTTP.OK)
       
@csrf_exempt
def RemoveSongLista(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
        idAudio = json_data[constantes.CLAVE_ID_AUDIO]
        idLista = json_data[constantes.CLAVE_ID_LISTA]
        
        # Control de errores
        if(usuarios.existeUsuario(r, idUsuario) == False):
            return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
        if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
            return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
        if(usuarios.existeLista(r, idLista) == False):
            return JsonResponse({'status': erroresHTTP.ERROR_LISTA_NO_ENCONTRADA}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
        if(moduloAudios.existeCancion(r, idAudio) == False):
            return JsonResponse({'status': erroresHTTP.ERROR_CANCION_NO_ENCONTRADA}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
        if(usuarios.isAudioFromLista(r, idLista, idAudio) == False):
            return JsonResponse({'status': erroresHTTP.ERROR_AUDIO_NOT_IN_LISTA}, status=erroresHTTP.ERROR_AUDIO_NOT_IN_LISTA)
        if(usuarios.isListaFromUser(r, idUsuario, idLista) == False):
            return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)

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
    
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    mensajeNotificacion = json_data[constantes.CLAVE_MENSAJE_NOTIFICACION]
    
    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.getTipoUsr(r, idUsuario) == constantes.USUARIO_ARTISTA):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_YA_ES_ARTISTA}, status=erroresHTTP.ERROR_USUARIO_YA_ES_ARTISTA)
    if(usuarios.getTipoUsr(r, idUsuario) == constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)

    usuarios.AskAdminToBeArtist(r, idUsuario, mensajeNotificacion)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

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
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]
   
    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeNotificacion(r, idNotificacion) == False):
        return JsonResponse({'error': 'La notificación no existe'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA)
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no es administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    if(usuarios.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA):
        return JsonResponse({'error': 'La notificación no es de tipo pedido de artista'}, status=erroresHTTP.ERROR_TIPO_NOTIFICACION_NO_VALIDA)
    if (usuarios.existeUsuario(r, usuarios.getUsuarioEmisorNotificacion(r, idNotificacion)) == False):
        return JsonResponse({'error': 'El usuario que ha enviado la notificación no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    usuarios.acceptArtist(r, idNotificacion)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def RejectArtista(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario and idNotificacion
    json_data = json.loads(request.body)
    
    # Primero valido que el usuario que me están pasando sea válido
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]
   
    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeNotificacion(r, idNotificacion) == False):
        return JsonResponse({'error': 'La notificación no existe'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA)
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no es administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    if(usuarios.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_SOLICITUD_ARTISTA):
        return JsonResponse({'error': 'La notificación no es de tipo pedido de artista'}, status=erroresHTTP.ERROR_TIPO_NOTIFICACION_NO_VALIDA)
    if (usuarios.existeUsuario(r, usuarios.getUsuarioEmisorNotificacion(r, idNotificacion)) == False):
        return JsonResponse({'error': 'El usuario que ha enviado la notificación no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    usuarios.rejectArtist(r, idNotificacion)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def ValidateUserEmail(request):
    return ValidateUser(request)

@csrf_exempt
def GetTotRepTime(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    weekday = json_data['dia']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
   
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'No eres administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    
    segundos = ModuloGlobal.getTotalSegundosReproducidosAudio(r, weekday)


    return JsonResponse({constantes.CLAVE_SECONDS: segundos}, status=erroresHTTP.OK)

@csrf_exempt
def AddSecondsToSong(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request bdoy to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    segundos = json_data[constantes.CLAVE_SECONDS]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La canción no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    if (segundos < 0):
        return JsonResponse({'error': 'Los segundos no pueden ser negativos'}, status=erroresHTTP.ERROR_SEGUNDOS_NEGATIVOS)

    ModuloGlobal.addSecondsToSong(r, idAudio, segundos)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)


def GetSongSeconds(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    weekday = json_data['dia']

    # Control de errores
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La canción no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    segundos = ModuloGlobal.getSongSecondsDia(r, idAudio, weekday)

    return JsonResponse({constantes.CLAVE_SECONDS: segundos}, status=erroresHTTP.OK)

@csrf_exempt
def SetFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    nombreCarpeta = json_data[constantes.CLAVE_NOMBRE_CARPETA]
    privacidad = json_data[constantes.CLAVE_PRIVACIDAD_CARPETA]
    diccionarioCarpeta = {constantes.CLAVE_NOMBRE_CARPETA: nombreCarpeta,
                          constantes.CLAVE_PRIVACIDAD_CARPETA: privacidad}

    #Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.carpetaPrivacidadValida(privacidad) == False):
        return JsonResponse({'error': 'La privacidad no es correcta'}, status=erroresHTTP.ERROR_CARPETA_PRIVACIDAD_NO_VALIDA)
    idFolder = usuarios.setFolder(r, idUsuario, diccionarioCarpeta)

    return JsonResponse({constantes.CLAVE_ID_CARPETA : idFolder}, status=erroresHTTP.OK)

@csrf_exempt
def AddListToFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no pertenece al usuario'}, status=erroresHTTP.ERROR_CARPETA_NOT_IN_USER)
    if(usuarios.isListaFromUser(r, idUsuario, idLista) == False):
        return JsonResponse({'error': 'La lista no pertenece al usuario'}, status=erroresHTTP.FORBIDDEN)
    if(usuarios.getTipoListaRep(r, idLista) == constantes.LISTA_TIPO_FAVORITOS):
        return JsonResponse({'error': 'La lista es de favoritos'}, status=erroresHTTP.ERROR_LISTA_ES_FAVORITOS)
    
    usuarios.addListToFolder(r, idUsuario, idCarpeta, idLista)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def RemoveListFromFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no pertenece al usuario'}, status=erroresHTTP.FORBIDDEN)
    if(usuarios.isListaFromCarpeta(r, idCarpeta, idLista) == False):
        return JsonResponse({'error': 'La lista no existe en la carpeta'}, status=erroresHTTP.ERROR_LISTA_NOT_IN_CARPETA)
    

    usuarios.removeListFromFolder(r, idCarpeta, idCarpeta)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def RemoveFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False):
        return JsonResponse({'error': 'No tienes permiso'}, status=erroresHTTP.FORBIDDEN)

    usuarios.removeFolder(r, idUsuario, idCarpeta)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def GetFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False and usuarios.isCarpetaPublica(r, idCarpeta) == False):
        return JsonResponse({'error': 'No tienes permiso'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse(usuarios.getFolder(r, idCarpeta), status=erroresHTTP.OK)

@csrf_exempt
def GetListasFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False and usuarios.isCarpetaPublica(r, idCarpeta) == False):
        return JsonResponse({'error': 'No tienes permiso'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse({constantes.CLAVE_ID_LISTA : usuarios.getListasFolder(r, idCarpeta)}, status=erroresHTTP.OK)

@csrf_exempt
def GetFoldersUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioGet = json_data[constantes.CLAVE_ID_USUARIO + "Get"]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False) and contrasenya != None:
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioGet) == False):
        if(usuarios.isSubscribedToArtist(r, idUsuario, idUsuarioGet)):
            usuarios.unsubscribeToArtist(r, idUsuario, idUsuarioGet)
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    if(idUsuario != idUsuarioGet):
        return JsonResponse({constantes.CLAVE_ID_CARPETA : usuarios.getPublicFoldersUser(r, idUsuario)}, status=erroresHTTP.OK)
    return JsonResponse({constantes.CLAVE_ID_CARPETA : usuarios.getFoldersUser(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def AskFriend(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAmigo = json_data[constantes.CLAVE_ID_AMIGO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idAmigo) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.isFriend(r, idUsuario, idAmigo) == True):
        return JsonResponse({'error': 'Ya sois amigos'}, status=erroresHTTP.ERROR_USUARIO_YA_AMIGO)
    
    usuarios.askFriend(r, idUsuario, idAmigo)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def AcceptFriend(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeNotificacion(r, idNotificacion) == False):
        return JsonResponse({'error': 'La notificacion no existe'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA)
    if(usuarios.existeUsuario(r, usuarios.getUsuarioEmisorNotificacion(r, idNotificacion)) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_AMIGO):
        return JsonResponse({'error': 'La notificacion no es de tipo amigo'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_AMIGO)
    if(usuarios.isFriend(r, idUsuario, usuarios.getUsuarioEmisorNotificacion(r, idNotificacion)) == True):
        return JsonResponse({'error': 'Ya sois amigos'}, status=erroresHTTP.ERROR_USUARIO_YA_AMIGO)

    usuarios.acceptFriend(r, idUsuario, idNotificacion)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def RejectFriend(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeNotificacion(r, idNotificacion) == False):
        return JsonResponse({'error': 'La notificacion no existe'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA)
    if(usuarios.existeUsuario(r, usuarios.getUsuarioEmisorNotificacion(r, idNotificacion)) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.getTipoNotificacion(r, idNotificacion) != constantes.NOTIFICACION_TIPO_AMIGO):
        return JsonResponse({'error': 'La notificacion no es de tipo amigo'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_AMIGO)
    if(usuarios.isFriend(r, idUsuario, usuarios.getUsuarioEmisorNotificacion(r, idNotificacion)) == True):
        return JsonResponse({'error': 'Ya sois amigos'}, status=erroresHTTP.ERROR_USUARIO_YA_AMIGO)

    usuarios.rejectFriend(r, idUsuario, idNotificacion)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

#@csrf_exempt
#def GetDataSong(r, idAudio):


# Devuelve un set con n ids de audios recuperadas mediante una búsqueda global
@csrf_exempt
def GetFriends(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
     
    return JsonResponse({constantes.CLAVE_ID_AMIGO : usuarios.getFriends(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def RemoveFriend(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAmigo = json_data[constantes.CLAVE_ID_AMIGO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idAmigo) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.isFriend(r, idUsuario, idAmigo) == False):
        return JsonResponse({'error': 'No sois amigos'}, status=erroresHTTP.ERROR_USUARIO_NO_AMIGO)
    
    usuarios.removeFriend(r, idUsuario, idAmigo)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def SubscribeToArtist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idArtista = json_data[constantes.CLAVE_ID_USUARIO + "Artista"]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idArtista) == False):
        return JsonResponse({'error': 'El artista no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.isSubscribedToArtist(r, idUsuario, idArtista) == True):
        return JsonResponse({'error': 'Ya estas suscrito a este artista'}, status=erroresHTTP.ERROR_USUARIO_YA_SUSCRITO)
    if(usuarios.getTipoUsr(r, idArtista) != constantes.USUARIO_ARTISTA):
        return JsonResponse({'error': 'El usuario no es un artista'}, status=erroresHTTP.ERROR_USUARIO_NO_ARTISTA)

    usuarios.subscribeToArtist(r, idUsuario, idArtista)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def UnsubscribeToArtist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idArtista = json_data[constantes.CLAVE_ID_USUARIO + "Artista"]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idArtista) == False):
        return JsonResponse({'error': 'El artista no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.isSubscribedToArtist(r, idUsuario, idArtista) == False):
        return JsonResponse({'error': 'No estas suscrito a este artista'}, status=erroresHTTP.ERROR_USUARIO_NO_SUSCRITO)

    usuarios.unsubscribeToArtist(r, idUsuario, idArtista)
    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def GetSubscriptionsUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
     
    return JsonResponse({constantes.CLAVE_ARTISTA_AUDIO : usuarios.getSubscriptionsUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def IsSubscribedToArtist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idArtista = json_data[constantes.CLAVE_ID_USUARIO + "Artista"]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idArtista) == False):
        return JsonResponse({'error': 'El artista no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.getTipoUsr(r, idArtista) != constantes.USUARIO_ARTISTA):
        return JsonResponse({'error': 'El usuario no es un artista'}, status=erroresHTTP.ERROR_USUARIO_NO_ARTISTA)
    
    return JsonResponse({'status': usuarios.isSubscribedToArtist(r, idUsuario, idArtista)}, status=erroresHTTP.OK)

@csrf_exempt
def GetNotificationsUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
     
    return JsonResponse({constantes.CLAVE_ID_NOTIFICACION : usuarios.getNotificationsUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def GetNotification(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeNotificacion(r, idNotificacion) == False):
        return JsonResponse({'error': 'La notificacion no existe'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA)
    if(usuarios.isNotificactionFromUser(r, idUsuario, idNotificacion) == False):
        return JsonResponse({'error': 'La notificacion no es tuya'}, status=erroresHTTP.FORBIDDEN)
     
    return JsonResponse({constantes.PREFIJO_NOTIFICACIONES : usuarios.getNotification(r, idNotificacion)}, status=erroresHTTP.OK)

@csrf_exempt
def RemoveNotification(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeNotificacion(r, idNotificacion) == False):
        return JsonResponse({'error': 'La notificacion no existe'}, status=erroresHTTP.ERROR_NOTIFICACION_NO_ENCONTRADA)
    if(usuarios.isNotificactionFromUser(r, idUsuario, idNotificacion) == False):
        return JsonResponse({'error': 'La notificacion no es tuya'}, status=erroresHTTP.FORBIDDEN)
    
    usuarios.removeNotification(r, idUsuario, idNotificacion)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def SetLastSecondHeared(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    segundo = json_data[constantes.CLAVE_SECONDS]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La cancion no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    if(segundo < 0):
        return JsonResponse({'error': 'El segundo no puede ser negativo'}, status=erroresHTTP.ERROR_SEGUNDOS_NEGATIVOS)

    usuarios.setLastSecondHeared(r, idUsuario,idAudio, segundo)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

@csrf_exempt
def GetLinkAudio(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'El audio no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    return JsonResponse({constantes.CLAVE_LINK_AUDIO : usuarios.getLinkAudio(r, idAudio)}, status=erroresHTTP.OK)

@csrf_exempt
def GetAudioFromLink(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    link = json_data[constantes.CLAVE_LINK_AUDIO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)

    
    return JsonResponse({constantes.PREFIJO_ID_LISTA : usuarios.getAudioFromLink(r, link)}, status=erroresHTTP.OK)

@csrf_exempt
def GetLastSecondHeared(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La cancion no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    return JsonResponse({constantes.CLAVE_SECONDS : usuarios.getLastSecondHeared(r, idUsuario,idAudio)}, status=erroresHTTP.OK)

@csrf_exempt
def GetSongsArtist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idArtista = json_data[constantes.CLAVE_ID_USUARIO + 'Artista']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idArtista) == False):
        if(usuarios.isSubscribedToArtist(r, idUsuario, idArtista)):
            usuarios.unsubscribeToArtist(r, idUsuario, idArtista)
        return JsonResponse({'error': 'El artista no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.getTipoUsr(r, idArtista) != constantes.USUARIO_ARTISTA):
        return JsonResponse({'error': 'El usuario no es un artista'}, status=erroresHTTP.ERROR_USUARIO_NO_ARTISTA)
    
    return JsonResponse({constantes.CLAVE_CANCIONES : usuarios.getCancionesArtista(r, idArtista)}, status=erroresHTTP.OK)

@csrf_exempt
def RemoveUser(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioEliminar = json_data[constantes.CLAVE_ID_USUARIO + 'Eliminar']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioEliminar) == False):
        return JsonResponse({'error': 'El usuario a eliminar no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(idUsuario != idUsuarioEliminar and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para eliminar este usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.removeUser(r, idUsuario)
    
    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetCauseError(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idError = json_data[constantes.CLAVE_ID_ERROR]

    return JsonResponse({'error': erroresHTTP.getError(idError)}, status=erroresHTTP.OK)

# Gets y Sets User
@csrf_exempt
def GetEmailUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioEmail = json_data[constantes.CLAVE_ID_USUARIO + '2']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioEmail) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)

    return JsonResponse({constantes.CLAVE_EMAIL : usuarios.getEmailUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def SetEmailUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioEmail = json_data[constantes.CLAVE_ID_USUARIO + '2']
    email = json_data[constantes.CLAVE_EMAIL]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioEmail) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.existeUsuarioEmail(r, email) == True):
        return JsonResponse({'error': 'El email ya existe'}, status=erroresHTTP.ERROR_USUARIO_EMAIL_YA_EXISTE)
    if(idUsuario != idUsuarioEmail and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar este usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.setEmailUsr(r, idUsuario, email)
    
    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetAliasUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioAlias = json_data[constantes.CLAVE_ID_USUARIO + '2']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioAlias) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)

    return JsonResponse({constantes.CLAVE_ALIAS : usuarios.getAliasUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def SetAliasUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioAlias = json_data[constantes.CLAVE_ID_USUARIO + '2']
    alias = json_data[constantes.CLAVE_ALIAS]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioAlias) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(idUsuario != idUsuarioAlias and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar este usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.setAliasUsr(r, idUsuario, alias)
    
    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetContrasenyaUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioContrasenya = json_data[constantes.CLAVE_ID_USUARIO + '2']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioContrasenya) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(idUsuario != idUsuarioContrasenya and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para obtener la contrsenya de este usuario'}, status=erroresHTTP.FORBIDDEN)

    return JsonResponse({constantes.CLAVE_CONTRASENYA : usuarios.getContrasenyaUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def SetContrasenyaUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioContrasenya = json_data[constantes.CLAVE_ID_USUARIO + '2']
    contrasenyaNueva = json_data[constantes.CLAVE_CONTRASENYA_NUEVA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioContrasenya) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(idUsuario != idUsuarioContrasenya and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar este usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.setContrasenyaUsr(r, idUsuario, contrasenyaNueva)
    
    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetTipoUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioTipo = json_data[constantes.CLAVE_ID_USUARIO + '2']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioTipo) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)

    return JsonResponse({constantes.CLAVE_TIPO_USUARIO : usuarios.getTipoUsr(r, idUsuario)}, status=erroresHTTP.OK)

@csrf_exempt
def SetTipoUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioTipo = json_data[constantes.CLAVE_ID_USUARIO + '2']
    tipoUsuario = json_data[constantes.CLAVE_TIPO_USUARIO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioTipo) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.tipoUsuarioValido(tipoUsuario) == False):
        return JsonResponse({'error': 'El tipo de usuario no es valido'}, status=erroresHTTP.ERROR_USUARIO_TIPO_NO_VALIDO)
    if(usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar este usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.setTipoUsr(r, idUsuario, tipoUsuario)
    
    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetImagenPerfilUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioImagen = json_data[constantes.CLAVE_ID_USUARIO + '2']

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioImagen) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    

    return JsonResponse({constantes.CLAVE_IMAGEN_PERFIL : usuarios.getImagenPerfilUsr(r, idUsuarioImagen)}, status=erroresHTTP.OK)

@csrf_exempt
def SetImagenPerfilUsr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idUsuarioImagen = json_data[constantes.CLAVE_ID_USUARIO + '2']
    imagenPerfil = json_data[constantes.CLAVE_IMAGEN_PERFIL]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeUsuario(r, idUsuarioImagen) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(idUsuario != idUsuarioImagen and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar este usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.setImagenPerfilUsr(r, idUsuario, imagenPerfil)
    
    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)


# Gets y Sets Lista
@csrf_exempt
def GetNombreListaRep(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR and 
       usuarios.isListaPublica(r, idLista) == False):
        return JsonResponse({'error': 'No tienes permisos para obtener el nombre de esta lista'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse({constantes.CLAVE_NOMBRE_CARPETA : usuarios.getNombreListaRep(r, idLista)}, status=erroresHTTP.OK)

def SetNombreListaRep(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]
    nombreLista = json_data[constantes.CLAVE_NOMBRE_LISTA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar esta lista'}, status=erroresHTTP.FORBIDDEN)
    
    usuarios.setNombreListaRep(r, idLista, nombreLista)

    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetPrivacidadListaRep(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if (usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR
         and usuarios.isListaPublica(r, idLista) == False):
        return JsonResponse({'error': 'No tienes permisos para obtener la privacidad de esta lista'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse({constantes.CLAVE_PRIVACIDAD_LISTA : usuarios.getPrivacidadListaRep(r, idLista)}, status=erroresHTTP.OK)

@csrf_exempt
def SetPrivacidadListaRep(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]
    privacidadLista = json_data[constantes.CLAVE_PRIVACIDAD_LISTA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if (usuarios.isListaFromUser(r, idUsuario, idLista) and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar esta lista'}, status=erroresHTTP.FORBIDDEN)
    if(usuarios.isListaPrivacidadValida(privacidadLista) == False):
        return JsonResponse({'error': 'La privacidad de la lista no es correcta'}, status=erroresHTTP.ERROR_LISTA_PRIVACIDAD_INCORRECTA)
    
    usuarios.setPrivacidadListaRep(r, idLista, privacidadLista)

    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

# Gets y Sets Carpeta
@csrf_exempt
def GetNombreCarpeta(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR
       and usuarios.isCarpetaPublica(r, idCarpeta) == False):
        return JsonResponse({'error': 'No tienes permisos para obtener el nombre de esta carpeta'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse({constantes.CLAVE_NOMBRE_CARPETA : usuarios.getNombreCarpeta(r, idCarpeta)}, status=erroresHTTP.OK)

def SetNombreCarpeta(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]
    nombreCarpeta = json_data[constantes.CLAVE_NOMBRE_CARPETA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar esta carpeta'}, status=erroresHTTP.FORBIDDEN)
    
    usuarios.setNombreCarpeta(r, idCarpeta, nombreCarpeta)

    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetPrivacidadCarpeta(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR
       and usuarios.isCarpetaPublica(r, idCarpeta) == False):
        return JsonResponse({'error': 'No tienes permisos para obtener la privacidad de esta carpeta'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse({constantes.CLAVE_PRIVACIDAD_CARPETA : usuarios.getPrivacidadCarpeta(r, idCarpeta)}, status=erroresHTTP.OK)

@csrf_exempt
def SetPrivacidadCarpeta(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]
    privacidadCarpeta = json_data[constantes.CLAVE_PRIVACIDAD_CARPETA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeCarpeta(r, idCarpeta) == False):
        return JsonResponse({'error': 'La carpeta no existe'}, status=erroresHTTP.ERROR_CARPETA_NO_ENCONTRADA)
    if(usuarios.isCarpetaFromUser(r, idUsuario, idCarpeta) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'error': 'No tienes permisos para modificar esta carpeta'}, status=erroresHTTP.FORBIDDEN)
    if(usuarios.carpetaPrivacidadValida(privacidadCarpeta) == False):
        return JsonResponse({'error': 'La privacidad de la carpeta no es válida'}, status=erroresHTTP.ERROR_CARPETA_PRIVACIDAD_NO_VALIDA)
    
    usuarios.setPrivacidadCarpeta(r, idCarpeta, privacidadCarpeta)

    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)

@csrf_exempt
def GetUsuarioListaRep(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)

    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    # Control de errores

    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista de reproducción no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    if(usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR 
       and usuarios.isListaPublica(r, idLista) == False):
        return JsonResponse({'error': 'No tienes permisos para obtener esta lista de reproducción'}, status=erroresHTTP.FORBIDDEN)
    
    return JsonResponse({constantes.CLAVE_ID_USUARIO : usuarios.getIDUsuarioListaRep(r, idLista)}, status=erroresHTTP.OK)

@csrf_exempt
def GetImagenAudio(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)

    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'El audio no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    return JsonResponse({constantes.CLAVE_IMAGEN_AUDIO : moduloAudios.getImagenAudio(r, idAudio)}, status=erroresHTTP.OK)

@csrf_exempt
def SetImagenAudio(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    imagenAudio = json_data[constantes.CLAVE_IMAGEN_AUDIO]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)

    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'El audio no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    moduloAudios.setImagenAudio(r, idAudio, imagenAudio)

    return JsonResponse({'status': 'OK'}, status=erroresHTTP.OK)


@csrf_exempt
def GlobalSearch(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    json_data = json.loads(request.body)
    query = json_data[constantes.CLAVE_QUERY]
    n = json_data[constantes.CLAVE_N]

    audios, artistas, listas = moduloAudios.buscarGeneral(r, query, int(n))

    #return JsonResponse({'status': status}, status=status)
    return JsonResponse({'audios': audios, 'artistas': artistas, 'listas': listas}, status=200)


@csrf_exempt
def ByWordSearch(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    querys = request.GET.get(constantes.CLAVE_QUERY)
    n = request.GET.get(constantes.CLAVE_N)    

    respuestas = []

    for query in querys:
        respuesta = moduloAudios.buscarCanciones(r, query, n)
        respuestas.append(respuesta)

    return JsonResponse({'datos': respuestas}, status=200)




@csrf_exempt
def GetRecomendedAudio(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)

    idUsr = json_data[constantes.CLAVE_ID_USUARIO]
    passwd = json_data[constantes.CLAVE_CONTRASENYA]

    status = usuarios.ValidateUser(r, idUsr, passwd)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    canciones = list(moduloAudios.obtenerTodasLasCanciones(r))
    podcasts = list(moduloAudios.obtenerTodosLosPodcasts(r))
    
    allAudios = []
    if len(canciones) > 0:
        allAudios.extend(canciones)
    if len(podcasts) > 0:
        allAudios.extend(podcasts)

    if len(allAudios) > 0:
        None
        idAudios = rec.orderAudios(r, idUsr, allAudios)     # Pide al recomendador que ordene los audios por relevancia
    else:
        idAudios = []
    
    #return JsonResponse({'status': status}, status=status)
    return JsonResponse({'idAudio': idAudios[0]}, status=200)


@csrf_exempt
def entrenar_recomendador(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'No eres administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    
    status = rec.train_model(r, nuevo_modelo=True)

    return JsonResponse({'status': status}, status=status)


@csrf_exempt
def AlmacenarEjemplo(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    idUsr = request.POST.get('idUsr')
    if idUsr == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    idAudio = request.POST.get('idAudio')
    if idAudio == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    valoracion = request.POST.get('valoracion')
    if valoracion == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    valoracion = float(valoracion)

    gen_datos.store_training_example(r, idUsr, idAudio, valoracion)

    return JsonResponse({'msg': 'Ejemplo almacenado correctamente'}, status=erroresHTTP.OK)


@csrf_exempt
def GetValoracion(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    
    idUsr = json_data[constantes.CLAVE_ID_USUARIO]
    if idUsr == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    if idAudio == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    valoracion = moduloAudios.getValoracion(r, idUsr, idAudio)

    if valoracion == None:
        valoracion = 0

    return JsonResponse({'valoracion': valoracion}, status=erroresHTTP.OK)


@csrf_exempt
def SetValoracion(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    
    idUsr = json_data[constantes.CLAVE_ID_USUARIO]
    if idUsr == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    if idAudio == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    valoracion = json_data[constantes.CLAVE_VALORACION]
    if valoracion == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    valoracion = float(valoracion)

    moduloAudios.setValoracion(r, idUsr, idAudio, valoracion)

    return JsonResponse({'msg': 'Valoración almacenada correctamente'}, status=erroresHTTP.OK)




@csrf_exempt
def GenerateRandomCodeUsr(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    emailUsuario = json_data[constantes.CLAVE_EMAIL]

    # Compruebo que el usuario existe
    if(usuarios.existeUsuarioEmail(r, emailUsuario)):

        # Generar número aleatorio
        code = random.randint(100000, 999999)
        usuarios.setCodigoRecuperacion(r, emailUsuario, code)

        
        # Configuración del servidor de correo electrónico y la cuenta
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = constantes.CORREO_RECUPERACION
        smtp_password = constantes.CONTRASENYA_CORREO_RECUPERACION

        # Configuración del correo electrónico
        from_email = smtp_username
        to_email = emailUsuario
        subject = "Recupera tu contraseña - Melodia"
        body = "Tu código de recuperación es el siguiente: " + str(code) + "\n\n" + "Si no has solicitado recuperar tu contraseña, ignora este correo."

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Agregar el cuerpo del correo electrónico
        msg.attach(MIMEText(body, 'plain'))

        # Conectar al servidor SMTP y enviar el correo electrónico
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())

        code = erroresHTTP.OK

    else:
        code = erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO


    return JsonResponse({'code': code}, status=erroresHTTP.OK)



@csrf_exempt
def SetCalidadPorDefectoUsr(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    passwd = json_data[constantes.CLAVE_CONTRASENYA]
    calidad = json_data[constantes.CLAVE_CALIDAD_PREFERIDA]

    # Contrlo de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.OK)
    if(usuarios.ValidateUser(r, idUsuario, passwd) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.OK)
    
    usuarios.setCalidadPorDefecto(r, idUsuario, calidad)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)


@csrf_exempt
def GetCalidadPorDefectoUsr(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    passwd = json_data[constantes.CLAVE_CONTRASENYA]

    # Contrlo de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.OK)
    if(usuarios.ValidateUser(r, idUsuario, passwd) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.OK)
    
    calidad = usuarios.getCalidadPorDefecto(r, idUsuario)
        
    return JsonResponse({'status': erroresHTTP.OK, 'calidad': calidad}, status=erroresHTTP.OK)

@csrf_exempt
def RecuperarContrasenya(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    emailUsuario = json_data[constantes.CLAVE_EMAIL]
    code = json_data[constantes.CLAVE_CODIGO_RECUPERACION]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    # Compruebo que el usuario existe
    if(usuarios.existeUsuarioEmail(r, emailUsuario)):
        # Compruebo que el código es correcto
        if(usuarios.getCodigoRecuperacion(r, emailUsuario) == code):

            # Obtengo la id del usuario
            idUsuario = usuarios.getIdEmailId(r, emailUsuario)
            usuarios.setContrasenya(r, idUsuario, contrasenya)
            code = erroresHTTP.OK
        else:
            code = erroresHTTP.ERROR_USUARIO_CODIGO_RECUPERACION_INCORRECTO
    else:
        code = erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO

    return JsonResponse({'code': code}, status=erroresHTTP.OK)
