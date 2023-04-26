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


from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

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
    fichero = -1
    # Compruebo que el método sea GET
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    id = request.GET.get(constantes.CLAVE_ID_AUDIO)
    calidadAlta = request.GET.get(constantes.CLAVE_FICHERO_ALTA_CALIDAD)
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
        response = usuarios.setUser(r, json_data)
        if response == 532 or response == 539:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=response)
        else:
            idUsuario = response.split(",")[1]
            diccionarioLista = {constantes.CLAVE_NOMBRE_LISTA : "Favoritos", 
                                constantes.CLAVE_PRIVACIDAD_LISTA : constantes.LISTA_PRIVADA, 
                                constantes.CLAVE_TIPO_LISTA : constantes.LISTA_TIPO_FAVORITOS}
            usuarios.setLista(r, idUsuario, diccionarioLista)
        
        return JsonResponse({'status': 200}, status=200)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        

@csrf_exempt
def GetUser(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        # Get the http parameters        
        idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
        contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

        # Validates the user
        status = usuarios.ValidateUser(r, idUsuario, contrasenya)
        if (status != erroresHTTP.OK):
            return JsonResponse({'status': status}, status=status)


        # Gets the user from the database
        response = usuarios.getUser(r, idUsuario)

        if response == 532 or response == 539:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=response)
        else:
            return JsonResponse(response, status=200)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def ValidateUser(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    email = json_data[constantes.CLAVE_EMAIL]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    respuesta = usuarios.validateUserEmail(r, email, contrasenya)
    if (respuesta["status"] != erroresHTTP.OK):
        return JsonResponse({'status': respuesta["status"]}, status=respuesta["status"])

    return JsonResponse({constantes.CLAVE_ID_USUARIO: respuesta[constantes.CLAVE_ID_USUARIO]}, status=respuesta["status"])

    
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
        status = usuarios.setLista(r, idUsuario, diccionarioLista)
        
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
    
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'El usuario no es administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    status = usuarios.acceptArtist(r, idNotificacion)

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
    if (respuesta["status"] != erroresHTTP.OK):
        return JsonResponse({'status': respuesta["status"]}, status=respuesta["status"])

    return JsonResponse({constantes.CLAVE_ID_USUARIO: respuesta[constantes.CLAVE_ID_USUARIO]}, status=respuesta["status"])



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
    
    #status = rec.create_model(r)

    return JsonResponse({'status': status}, status=status)



@csrf_exempt
def GetTotRepTime(request):
    if request.method != 'GET':
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
    
    segundos = ModuloGlobal.getTotalSegundosReproducidosAudio(r)


    return JsonResponse({constantes.CLAVE_SEGUNDOS: segundos}, status=erroresHTTP.OK)

@csrf_exempt
def AddSecondsToSong(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    segundos = json_data[constantes.CLAVE_SEGUNDOS]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    if(moduloAudios.existeCancion(r, idAudio) == False):
        return JsonResponse({'error': 'La canción no existe'}, status=erroresHTTP.ERROR_CANCION_NO_ENCONTRADA)
    
    status = ModuloGlobal.addSecondsToSong(r, idAudio, segundos)

    return JsonResponse({'status': status}, status=status)

@csrf_exempt
def GetLista(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idLista = json_data[constantes.CLAVE_ID_LISTA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    if(usuarios.existeLista(r, idLista) == False):
        return JsonResponse({'error': 'La lista no existe'}, status=erroresHTTP.ERROR_LISTA_NO_ENCONTRADA)
    
    respuesta = usuarios.getListaRepUsr(r, idLista)

    if(respuesta["status"] != erroresHTTP.OK):
        return JsonResponse({'status': respuesta["status"]}, status=respuesta["status"])
    
    return JsonResponse({constantes.PREFIJO_ID_LISTA : respuesta[constantes.PREFIJO_ID_LISTA]}, status=erroresHTTP.OK)

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

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.setFolder(r, diccionarioCarpeta)

    return JsonResponse({'status': status}, status=status)

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

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.addListToFolder(r, idLista, idCarpeta)

    return JsonResponse({'status': status}, status=status)

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

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.removeListFromFolder(r, idLista, idCarpeta)

    return JsonResponse({'status': status}, status=status)

@csrf_exempt
def RemoveFolder(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.removeFolder(r, idCarpeta)

    return JsonResponse({'status': status}, status=status)

@csrf_exempt
def GetFolder(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idCarpeta = json_data[constantes.CLAVE_ID_CARPETA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    respuesta = usuarios.getFolder(r, idCarpeta)

    if(respuesta["status"] != erroresHTTP.OK):
        return JsonResponse({'status': respuesta["status"]}, status=respuesta["status"])
    
    return JsonResponse({constantes.PREFIJO_ID_CARPETA : respuesta[constantes.PREFIJO_ID_CARPETA]}, status= respuesta["status"])

@csrf_exempt
def GetFoldersUsr(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    respuesta = usuarios.getFoldersUser(r, idUsuario)

    if(respuesta["status"] != erroresHTTP.OK):
        return JsonResponse({'status': respuesta["status"]}, status=respuesta["status"])
    
    return JsonResponse({constantes.PREFIJO_ID_CARPETA : respuesta[constantes.PREFIJO_ID_CARPETA]}, status= respuesta["status"])

@csrf_exempt
def AskFriend(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idAmigo = json_data[constantes.CLAVE_ID_AMIGO]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.askFriend(r, idUsuario, idAmigo)

    return JsonResponse({'status': status}, status=status)

@csrf_exempt
def AcceptFriend(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]
    idNotificacion = json_data[constantes.CLAVE_ID_NOTIFICACION]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if (status != erroresHTTP.OK):
        return JsonResponse({'status': status}, status=status)
    
    status = usuarios.accpetFriend(r, idUsuario, idNotificacion)

    return JsonResponse({'status': status}, status=status)

#@csrf_exempt
#def GetDataSong(r, idAudio):


# Devuelve un set con n ids de audios recuperadas mediante una búsqueda global
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
        #idAudios = rec.orderAudios(r, idUsr, allAudios)     # Pide al recomendador que ordene los audios por relevancia
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
    
    #status = rec.create_model(r)

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

