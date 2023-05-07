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

# View para pruebas
@csrf_exempt
def FlushDB(request):
    r.flushdb()
    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

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
    # Compruebo que el método sea POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    jsonData = json.loads(request.body)
    idAudio = jsonData[constantes.CLAVE_ID_AUDIO]
    idUsuario = jsonData[constantes.CLAVE_ID_USUARIO]
    contrasenya = jsonData[constantes.CLAVE_CONTRASENYA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)

    # Si no es valido devuelvo el error
    if (status == False):
        return JsonResponse({'status': status}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
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

    # Control de errores
    if(usuarios.existeUsuarioEmail(r, email)):
        return JsonResponse({'error': 'El email ya existe'}, status=erroresHTTP.ERROR_USUARIO_EMAIL_YA_EXISTE)
    
    if(usuarios.correctoDiccionarioUsuario(json_data) == False):
        return JsonResponse({'error': 'El diccionario no es correcto'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    if(usuarios.tipoUsuarioValido(json_data[constantes.CLAVE_TIPO_USUARIO]) == False):
        return JsonResponse({'error': 'El tipo de usuario no es valido'}, status=erroresHTTP.ERROR_USUARIO_TIPO_NO_VALIDO)
    
    # No error, so add the user
    idUsuario = usuarios.setUser(r, json_data)

    diccionarioLista = {constantes.CLAVE_NOMBRE_LISTA : "Favoritos", 
                        constantes.CLAVE_PRIVACIDAD_LISTA : constantes.LISTA_PRIVADA, 
                        constantes.CLAVE_TIPO_LISTA : constantes.LISTA_TIPO_FAVORITOS}
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

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False and contrasenya != None):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if(contrasenya == None):
        return JsonResponse(usuarios.getUserPublicData(r, idUsuario), status=erroresHTTP.OK)
    return JsonResponse(usuarios.getUser(r, idUsuario), status=erroresHTTP.OK)

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
    diccionarioLista = json_data.copy()
    del diccionarioLista[constantes.CLAVE_ID_USUARIO]
    del diccionarioLista[constantes.CLAVE_CONTRASENYA]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    # Validates the user
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if (usuarios.correctoDiccionarioLista(diccionarioLista) == False):
        return JsonResponse({'error': 'El diccionario no es correcto'}, status=erroresHTTP.ERROR_LISTA_PARAMETROS_INCORRECTOS)
    if (usuarios.listaPrivacidadValida(diccionarioLista[constantes.CLAVE_PRIVACIDAD_LISTA]) == False):
        return JsonResponse({'error': 'La privacidad no es valida'}, status=erroresHTTP.ERROR_LISTA_PRIVACIDAD_INCORRECTA)
    if (usuarios.tipoListaValido(diccionarioLista[constantes.CLAVE_TIPO_LISTA]) == False):
        return JsonResponse({'error': 'El tipo de lista no es valido'}, status=erroresHTTP.ERROR_LISTA_TIPO_INCORRECTO)

    idLista = usuarios.setLista(r, idUsuario, diccionarioLista)
    return JsonResponse({constantes.CLAVE_ID_LISTA: idLista}, status=erroresHTTP.OK)
    
    
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
    usuarios.setNombreLista(r, idLista, nombre)
    
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
    usuarios.setSongLista(r, idLista, idAudio)
    
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

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False and contrasenya != None):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if (contrasenya == None):
        return JsonResponse({constantes.CLAVE_LISTAS: usuarios.getListasUsrPublicas(r, idUsuario)}, status=erroresHTTP.OK)
    return JsonResponse({constantes.CLAVE_LISTAS: usuarios.getListasUsr(r, idUsuario)}, status=erroresHTTP.OK)
       
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
    
    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if (usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'status': erroresHTTP.ERROR_CONTRASENYA_INCORRECTA}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    if(usuarios.getTipoUser(r, idUsuario) == constantes.USUARIO_ARTISTA):
        return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_YA_ES_ARTISTA}, status=erroresHTTP.ERROR_USUARIO_YA_ES_ARTISTA)
    if(usuarios.getTipoUser(r, idUsuario) == constantes.USUARIO_ADMINISTRADOR):
        return JsonResponse({'status': erroresHTTP.FORBIDDEN}, status=erroresHTTP.FORBIDDEN)

    usuarios.AskAdminToBeArtist(r, idUsuario)

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

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
   
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'No eres administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    
    segundos = ModuloGlobal.getTotalSegundosReproducidosAudio(r)


    return JsonResponse({constantes.CLAVE_SEGUNDOS: segundos}, status=erroresHTTP.OK)

@csrf_exempt
def AddSecondsToSong(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request bdoy to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    segundos = json_data[constantes.CLAVE_SEGUNDOS]

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False):
        return JsonResponse({'error': 'La contraseña es incorrecta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La canción no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    if (segundos < 0):
        return JsonResponse({'error': 'Los segundos no pueden ser negativos'}, status=erroresHTTP.ERROR_SEGUNDOS_NEGATIVOS)

    status = ModuloGlobal.addSecondsToSong(r, idAudio, segundos)

    return JsonResponse({'status': status}, status=status)


def GetSongSeconds(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request bdoy to extract idUsuario
    idAudio = request.GET.get(constantes.CLAVE_ID_AUDIO)

    # Control de errores
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La canción no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    segundos = ModuloGlobal.getSongSeconds(r, idAudio)

    return JsonResponse({constantes.CLAVE_SEGUNDOS: segundos}, status=erroresHTTP.OK)

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
    if(usuarios.correctoDiccionarioCarpeta(diccionarioCarpeta) == False):
        return JsonResponse({'error': 'El diccionario de la carpeta no es correcto'}, status=erroresHTTP.ERROR_CARPETA_PARAMETROS_INCORRECTOS)
    if(usuarios.carpetaPrivacidadValida(privacidad) == False):
        return JsonResponse({'error': 'La privacidad no es correcta'}, status=erroresHTTP.ERROR_CARPETA_PRIVACIDAD_NO_VALIDA)
    usuarios.setFolder(r, idUsuario, diccionarioCarpeta)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

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
    if(usuarios.isListaFromUser(r, idUsuario, idLista) == False and usuarios.isListaPublica(r, idLista) == False):
        return JsonResponse({'error': 'La lista no pertenece al usuario'}, status=erroresHTTP.FORBIDDEN)

    usuarios.addListToFolder(r, idCarpeta, idLista)

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
    if request.method != 'GET':
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

    # Control de errores
    if(usuarios.existeUsuario(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no existe'}, status=erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO)
    if(usuarios.ValidateUser(r, idUsuario, contrasenya) == False) and contrasenya != None:
        return JsonResponse({'error': 'La contraseña no es correcta'}, status=erroresHTTP.ERROR_CONTRASENYA_INCORRECTA)
    
    if(contrasenya == None):
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
    if(usuarios.getTipoUser(r, idArtista) != constantes.USUARIO_ARTISTA):
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
    segundo = json_data[constantes.CLAVE_SEGUNDOS]

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
    
    return JsonResponse({constantes.CLAVE_SEGUNDOS : usuarios.getLastSecondHeared(r, idUsuario,idAudio)}, status=erroresHTTP.OK)


@csrf_exempt
def GlobalSearch(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    query = request.GET.get(constantes.CLAVE_QUERY)
    n = request.GET.get(constantes.CLAVE_N)    

    respuesta = moduloAudios.buscarCanciones(r, query, n)

    #return JsonResponse({'status': status}, status=status)
    return JsonResponse({'datos': respuesta}, status=200)

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
def GenerateRandomCodeUsr(request):
    # Compruebo que el método sea GET
    if request.method != 'GET':
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
        subject = "Correo electrónico de prueba"
        body = "Este es un correo electrónico de prueba enviado desde Python."

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
            usuarios.setContrasenya(r, emailUsuario, contrasenya)
            code = erroresHTTP.OK
        else:
            code = erroresHTTP.ERROR_USUARIO_CODIGO_RECUPERACION_INCORRECTO
    else:
        code = erroresHTTP.ERROR_USUARIO_NO_ENCONTRADO

    return JsonResponse({'code': code}, status=erroresHTTP.OK)