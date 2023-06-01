from django.shortcuts import render
from django.http import JsonResponse
import json
import redis

from Configuracion import constantesPrefijosClaves as constantes
from Configuracion import constantesErroresHTTP as erroresHTTP

from Audios import moduloAudios
from Usuarios import usuarios

from recomendador import generacion_datos as gen_datos
from recomendador import recomendador as rec

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
# La función echo no está en la API
@csrf_exempt
def echo(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)
        
        return JsonResponse(json_data)
    else:
        # Return a 405 Method Not Allowed response for other HTTP methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si el audio existe en la calidad requerida, devuelve un VO audio completo.
# Si existe en otra calidad, la devuelve en esa calidad
# Si el usuario no es tipo artista devuelve ERROR_USUARIO_NO_ARTISTA
# Si no existe, devuelve código error 519 en el caso de canciones y 525 en el caso de podcast
# Sintaxis de la función: GetSong(String idUsr, String contrasenya, String idAudio) : Song
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

    audio["nReproducciones"] = moduloAudios.getReproducciones(r, idAudio)

    gen_datos.add_audio_prediction_temporal(r, idUsuario, idAudio)

    return JsonResponse({constantes.CLAVE_ID_AUDIO: audio}, status=erroresHTTP.OK)
    
# La función GetFicheroSong no está en la API
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

    if fichero == 419 or fichero == 424 or fichero == 430 or fichero == 425 or fichero == 519 or fichero == 524:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=fichero)
    else:
        idUsr = request.GET.get('idUsr')
        if idUsr == None:
            return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
        
        # Gets the serialized audio
        return JsonResponse({'fichero': fichero})


# Como getSong, pero devuelve un bloque con varios audios
# Sintaxis de la función: GetSongs(String idUsr, List<String> idAudios, Bool calidadAlta, Bool esCancion) : Set<String>
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

# Si el usuario no existe devuelve -2
# En caso contrario:
# Si el usuario no tiene permisos para crear audios devuelve -3
# En caso contrario:
# Almacena un audio y devuelve status 200
# Song es de tipo diccionario definido anteriormente al principio del documento
# Sintaxis de la función: SetSong(String contrasenya, String idUsr, Song song) : int
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
    if (usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ARTISTA and usuarios.getTipoUsr(r, idUsuario) != constantes.USUARIO_ADMINISTRADOR):
       return JsonResponse({'status': erroresHTTP.ERROR_USUARIO_NO_ARTISTA}, status=erroresHTTP.ERROR_USUARIO_NO_ARTISTA)

    if status == True:

        # Añado la canción a la base de datos
        id = moduloAudios.anyadirCancion(r, json_data)
        usuarios.anyadirNotificacionSubidaCancion(r, idUsuario, id)
        

        return JsonResponse({constantes.CLAVE_ID_AUDIO: id}, status=erroresHTTP.OK)
    else:
        return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)

# Si todo va bien crea un usuario con los datos de usr, crea su lista favoritos y devuelve OK,
# Si el email del usuario ya está siendo usado por algún usuario de la base de datos
# devuelve ERROR_USUARIO_EMAIL_YA_EXISTE
# Si el tipo de usuario no es válido devuelve ERROR_USUARIO_TIPO_NO_VALIDO
# Sintaxis de la función: SetUser(email, alias, contrasenya, tipoUsuario) : int
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida y no nula para ese usuario devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# En caso contrario
# Si son el mismo usuario devuelve toda la información del usuario 
# Si no solo devuelve la información pública del usuario ‘Get’
# Sintaxis de la función: GetUser(Strting idUsr, String contrasenya, String idUsrGet): DiccUsr
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

# Si el usuario no existe, devuelve ERROR_USUARIO_NO_ENCONTRADO
# En caso contrario:
# Si la contraseña es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si no, devuelve OK
# Sintaxis de la función: ValidateUser(String email, String contrasenya) : int
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

    
# La función SetLista no está en la API
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
    
    


# Devuelve un set con los n audios con mayor número de reproducciones
# Sintaxis de la función: GetTopReproducciones(Int n, Bool esPodcast) : Set<String> topAudios
@csrf_exempt
def GetTopReproducciones(request):

    if request.method != 'POST':
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
    print(pairs)
    # sort the pairs based on the values in the second list (i.e. b)
    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    # extract the first element of each pair (i.e. the elements of a) into a new list
    audios_ordenados = [pair[0] for pair in sorted_pairs]

    return JsonResponse({'topAudios': audios_ordenados[0:n]}, status=200)

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCOTRADA
# Si el usuario no le pertenece esa lista devuelve FORBIDDEN
# En caso contrario cambia el nombre de la lista y devuelve OK
# Sintaxis de la función: ChangeNameListRepUsr(String idUsr, String contrasenya, String idLista, String nombreLista): int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista de reproducción existe, devuelve un diccionario con sus datos
# Si no existe devuelve ERROR_LISTA_NO_ENCONTRADA
# Si la lista no pertenece al usuario y es privada devuelve FORBIDDEN
# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# En caso contrario:
# Si la lista de reproducción existe, añade el audio y devuelve OK
# Si no existe devuelve ERROR_LISTA_NO_ENCONTRADA
# Si no existe el audio devuelve ERROR_AUDIO_NO_ENCONTRADO
# Si la lista no pertenece al usuario devuelve FORBIDDEN
# Sintaxis de la función: SetSongLista(String idUsr, String contrasenya, String idLista, String idAudio): int	
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

# La función GetLista no está en la API
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


# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# En caso contrario:
# Si son el mismo usuario devuelve un set con las ids de todas las listas de reproducción del # usuario que no están en una carpeta
# Si no devuelve un set con las ids de las listas de reproducción públicas que no están en 
# una carpeta
# Sintaxis de la función: GetListasUsr(String idUsr, String contrasenya, idUsrGet): Set<String>
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCONTRADA
# Si la carpeta es tipo favoritos devuelve ERROR_LISTA_ES_FAVORITOS
# En caso contrario elimina la lista
# Sintaxis de la función: RemoveListaRepUsr(String idUsr, String contrasenya, String idLista): int
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

       
# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no pertenece al usuario y es privada devuelve FORBIDDEN
# En caso contrario:
# Devuelve un set con las ids de todas las canciones en la lista del usuario
# Sintaxis de la función: GetAudiosLista(String idUsr, String contrasenya, String idLista): Set<String>
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
       
# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si no existe la lista, devuelve ERROR_LISTA_NO_ENCOTRADA
# Si no existe el audio, devuelve ERROR_AUDIO_NO_ENCONTRADO
# Si el audio no pertenece a la lista, devuelve ERROR_AUDIO_NOT_IN_LISTA
# Si la lista no pertenece al usuario devuelve FORBIDDEN
# En caso contrario:
# Si la lista existe, elimina el audio de la misma y devuelve OK
# Sintaxis de la función: RemoveSongLista(String idUsr, String contrasenya, String idLista, String idAudio): int
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
    
# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida para ese usuario devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el usuario ya es artista devuelve ERROR_USUARIO_YA_ES_ARTISTA
# Si el usuario es admin devuelve FORBIDDEN
# En caso contrario
# Envía una petición al administrador para convertirse en artista y devuelve OK
# Sintaxis de la función: AskAdminToBeArtist(String idUsr, String contrasenya, String mensaje) : int
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

# Si existe una petición del usuario usr para convertirse en artista
# Convierte a usr en artista y devuelve OK
# Si no, devuelve ERROR_NOTIFICACION_NO_ENCOTRADA si la notificación no se ha 
# encontrado, ERROR_TIPO_NOTIFICACION_NO_VALIDA si el tipo de notificación no es 
# válida
# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA 
# Si el usuario no es administrador devuelve ERROR_USUARIO_NO_ADMINISTRADOR
# Sintaxis de la función: AcceptArtist(String contrasenya, String idUsr, String idNotificacion) : int
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

# La función RejectArtista no está en la API
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

# Hace lo mismo que ValidateUser, pero tiene como parámetro el email y no el id del usuario
# Sintaxis de la función: ValidateUserEmail(String email, String contrasenya) : int
@csrf_exempt
def ValidateUserEmail(request):
    return ValidateUser(request)

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si el usuario no es administrador devuelve ERROR_USUARIO_NO_ADMINISTRADOR
# dia = int del 0 al 6, siendo 0 lunes, …, 6 domingo.
# En caso contrario:
# Devuelve el número total de segundos de audio reproducidos en ese dia
# Sintaxis de la función: GetTotRepTime(String idUsr, String contrasenya, int dia) : int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCOTRADA
# Si los segundos son negativos devuelve ERROR_SEGUNDOS_NEGATIVOS
# En caso contrario:
# Añade seconds segundos de reproducción al audio
# Sintaxis de la función: AddSecondsToSong(String idUsr, String contrasenya, String idSong, int seconds) : int
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
    
    if (int(segundos) < 0):
        return JsonResponse({'error': 'Los segundos no pueden ser negativos'}, status=erroresHTTP.ERROR_SEGUNDOS_NEGATIVOS)

    ModuloGlobal.addSecondsToSong(r, idAudio, segundos)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)


# Si el audio no existe devuelve ERROR_CANCION_NO_ENCOTRADA
# dia = int del 0 al 6, siendo 0 lunes, …, 6 domingo.
# Devuelve el número total de segundos reproducidos del audio en ese dia
# Sintaxis de la función: GetSongSeconds(idAudio, dia): None
@csrf_exempt
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la privacidad no es válida devuelve ERROR_CARPETA_PRIVACIDAD_NO_VALIDA
# En caso contrario:
# Crea una carpeta con los datos y devuelve OK
# Sintaxis de la función: SetFolder(String idUsr, String contrasenya, String nombreCarpeta, String privacidadCarpeta): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCONTRADA
# SI la carpeta no existe devuelve ERROR_CARPETA_NO_ENCONTRADA
# Si la carpeta no pertenece al usuario devuelve ERROR_CARPETA_NOT_IN_USER
# Si la carpeta es tipo favoritos devuelve ERROR_LISTA_ES_FAVORITOS
# Si la lista no pertenece al usuario y no es pública devuelve FORBIDDEN
# En caso contrario:
# Añade la lista a la carpeta, quita la lista de las listas sin carpeta del usuario y devuelve OK
# Sintaxis de la función: AddListToFolder(String idUsr, String contrasenya, String idCarpeta, String idLista) : int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCONTRADA
# SI la carpeta no existe devuelve ERROR_CARPETA_NO_ENCONTRADA
# SI la lista no está en la carpeta devuelve ERROR_LISTA_NOT_IN_CARPETA
# Si la carpeta no pertenece al usuario devuelve FORBIDDEN
# En caso contrario:
# Elimina la lista de reproducción de la carpeta
# Sintaxis de la función: RemoveListFromFolder(String idUsr, String contrasenya, String idCarpeta, String idLista): int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la carpeta no existe devuelve ERROR_CARPETA_NO_ENCONTRADA
# Si la carpeta no pertenece al usuario FORBIDDEN
# En caso contrario:
# Elimina la carpeta y las listas dentro de ella
# Sintaxis de la función: RemoveFolder(String idUsr, String contrasenya, String idCarpeta): int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# SI la carpeta no existe devuelve ERROR_CARPETA_NO_ENCONTRADA
# Si la carpeta no pertenece al usuario y es privada devuelve FORBIDDEN
# En caso contrario:
# Devuelve un diccionario con los datos de carpeta
# Sintaxis de la función: GetFolder(String idUsr, String contrasenya, String idCarpeta) : int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# SI la carpeta no existe devuelve ERROR_CARPETA_NO_ENCONTRADA
# Si la carpeta no pertenece al usuario y es privada devuelve FORBIDDEN
# En caso contrario:
# Devuelve un set con los ids de las listas
# Sintaxis de la función: GetListasFolder(String idUsr, String contrasenya, String idCarpeta): set<String>
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

# Si uno  de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# En caso contrario:
# Si son el mismo usuario devuelve un set con las ids de todas las carpetas del usuario
# Si no devuelve un set con las ids de las carpetas públicas del usuario ‘Get’
# Sintaxis de la función: GetFoldersUsr(String idUsr, String contrasenya, String idUsrGet) : Set<String>
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

# Si alguno de los dos usuarios no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si ya son amigos devuelve ERROR_USUARIO_YA_AMIGO
# En caso contrario:
# Envía una notificación de amistad a friend y devuelve OK
# Sintaxis de la función: AskFriend(String idUsr, String contrasenya, String idAmigo) : int
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

# Si alguno de los dos usuarios no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si no existe la notificación devuelve ERROR_NOTIFICACIO_NO_ENCONTRADA
# En caso contrario:
# Si la notificación no es de amistad devuelve ERROR_NOTIFICACION_NO_AMIGO
# Si no acepta la amistad, elimina la notificación y devuelve OK
# Sintaxis de la función: AcceptFriend(String idUsr, String contrasenya, String idNotifiacion): int
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

# Si alguno de los dos usuarios no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si no existe la notificación devuelve ERROR_NOTIFICACIO_NO_ENCONTRADA
# En caso contrario:
# Si la notificación no es de amistad devuelve ERROR_NOTIFICACION_NO_AMIGO
# Si no rechaza la amistad, elimina la notificación y devuelve OK
# Sintaxis de la función: RejectFriend(String idUsr, String contrasenya, String idNotifiacion): int
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


# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# En caso contrario:
# Devuelve el id de todos sus amigos
# Sintaxis de la función: GetFriends(String idUsr, String contrasenya): Set<String>
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

# Si alguno de los dos usuarios no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si los usuarios no son amigos devuelve ERROR_USUARIO_NO_AMIGO
# En caso contrario:
# Ambos usuarios eliminan su amistad entre ellos y devuelve OK
# Sintaxis de la función: RemoveFriend(String idUsr, String contrasenya, String idAmigo): int
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

# Si el usuario o el artista no existen devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si el usuario ya está suscrito devuelve ERROR_USUARIO_YA_SUSCRITO
# Si el usuario artista no es tipo artista devuelve ERROR_USUARI_NO_ARTISTA
# En caso contrario:
# Añade al artista a la lista de suscripciones del usuario
# Sintaxis de la función: SubscribeToArtist(String idUsr, String contrasenya, String idUsrArtista) : int
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

# La función UnsubscribeToArtist no está en la API
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# En caso contrario devuelve un set de ids de los artistas a los que está suscrito
# Sintaxis de la función: GetSubscriptionsUsr(idUsr, contrasenya): None
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

# Si el usuario o el artista no existen devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si el usuario idUsrArtista no es artista devuelve ERROR_USUARIO_NO_ARTISTA
# En caso contrario devuelve 1 si está suscrito sino 0
# Sintaxis de la función: IsSubscribedToArtist(idUsr, contrasenya, idUsrArtista): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# En caso contrario:
# Devuelve un set con las ids de todas las notificaciones del usuario
# Sintaxis de la función: GetNotificationsUsr(String idUsr, String contrasenya) : Set<String>
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la notificación no existe devuelve ERROR_NOTIFIACION_NO_ENCONTRADA
# Si la notificación no pertenece al usuario devuelve FORBIDDEN
# En caso contrario: Devuelve un diccionario de la notificación
# Sintaxis de la función: GetNotification(String idUsr, String contrasenya, String idNotificacion): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es correcta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la notificación no existe devuelve ERROR_NOTIFIACION_NO_ENCONTRADA
# Si la notificación no pertenece al usuario devuelve FORBIDDEN
# En caso contrario:
# Elimina la notificación del usuario
# Sintaxis de la función: RemoveNotification(String idUsr, String contrasenya, idNotificacion) : Set<String>
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

# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida para ese usuario devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCONTRADA
# En caso contrario
# Almacena el último segundo escuchado del audio
# Sintaxis de la función: SetLastSecondHeared(String idUsr, String contrasenya, String idAudio, int second) : int
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
    if(int(segundo) < 0):
        return JsonResponse({'error': 'El segundo no puede ser negativo'}, status=erroresHTTP.ERROR_SEGUNDOS_NEGATIVOS)

    usuarios.setLastSecondHeared(r, idUsuario,idAudio, segundo)

    return JsonResponse({'status': erroresHTTP.OK}, status=erroresHTTP.OK)

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCONTRADA
# En caso contrario devuelve un link del idAudio
# Sintaxis de la función: GetLinkAudio(String idUsr, String contrasenya, String idAudio) : string
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCONTRADA
# En caso contrario devuelve un id del audio dado el link
# Sintaxis de la función: GetAudioFromLink(String idUsr, String contrasenya, String linkAudio) : string
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

# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida para ese usuario devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCONTRADA
# En caso contrario
# Devuelve el último segundo escuchado del audio
# Sintaxis de la función: GetLastSecondHeared(String idUsr, String contrasenya, String idAudio) : int second
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

# Si el usuario no existe devuelve -2 
# En caso contrario:
# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si el idUsrArtista no es artista devuelve ERROR_USUARIO_NO_ARTISTA
# En caso contrario devuelve un set de ids de las canciones del artista
# Sintaxis de la función: GetSongsArtist(idUsr, contrasenya, idUsrArtista) : Set<String>
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si los usuarios son distintos y idUsr no es tipo administrador devuelve FORBIDDEN
# En caso contrario elimina el usuario
# Sintaxis de la función: RemoveUser(String idUsr, String contrasenya, String idUsrEliminar) : int
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

# Devuelve un string con información sobre el error comprensible para humanos
# Sintaxis de la función: GetCauseError(int idError) : String
@csrf_exempt
def GetCauseError(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    idError = json_data[constantes.CLAVE_ID_ERROR]

    return JsonResponse({'error': erroresHTTP.getError(idError)}, status=erroresHTTP.OK)

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# En caso contrario devuelve el email de idUsr2
# Sintaxis de la función: GetEmailUsr(idUsr, contrasenya, idUsr2): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si un usuario con ese email ya existe devuelve ERROR_USUARIO_EMAIL_YA_EXISTE
# Si los usuarios no son los mismos y idUsr no es administrador devuelve FORBIDDEN
# En caso contrario cambia el email de idUsr2
# Sintaxis de la función: SetEmailUsr(idUsr, contrasenya, idUsr2, email): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# En caso contrario devuelve el alias de idUsr2
# Sintaxis de la función: GetAliasUsr(idUsr, contrasenya, idUsr2): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si los usuarios no son los mismos y idUsr no es administrador devuelve FORBIDDEN
# En caso contrario cambia el email de idUsr2
# Sintaxis de la función: SetAliasUsr(idUsr, contrasenya, idUsr2, alias): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# En caso contrario devuelve la contrasenya de idUsr2
# Sintaxis de la función: GetContrasenyaUsr(idUsr, contrasenya, idUsr2): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si los usuarios no son los mismos y idUsr no es administrador devuelve FORBIDDEN
# En caso contrario cambia la contrasenya de idUsrContrasenya
# Sintaxis de la función: SetContrasenyaUsr(idUsr, contrasenya, idUsr2): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# En caso contrario devuelve el tipo de usuario de idUsr2
# Sintaxis de la función: GetTipoUsr(idUsr, contrasenya, idUsr2): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si tipoUsuario no es válido devuelve ERROR_USUARIO_TIPO_NO_VALIDO
# Si los usuarios no son los mismos y idUsr no es administrador devuelve FORBIDDEN
# En caso contrario cambia el tipoUsuario de idUsr2
# Sintaxis de la función: SetTipoUsr(idUsr, contrasenya, idUsr2, tipoUsuario): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# En caso contrario devuelve la imagen de perfil de idUsr2
# Sintaxis de la función: GetImagenPerfilUsr(idUsr, contrasenya, idUsr2): None
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

# Si uno de los usuarios no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve u
# ERROR_CONTRASENYA_INCORRECTA
# Si tipoUsuario no es válido devuelve ERROR_USUARIO_TIPO_NO_VALIDO
# Si los usuarios no son los mismos y idUsr no es administrador devuelve FORBIDDEN
# En caso contrario cambia la imagen de idUsr2
# Sintaxis de la función: SetImagenPerfilUsr(idUsr, contrasenya, idUsr2, imagen): None
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


# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCOTRADA
# Si el usuario no le pertenece esa lista y no es administrador y no es una lista 
# pública devuelve FORBIDDEN
# En caso contrario devuelve el nombre de la lista
# Sintaxis de la función: GetNombreListaRep(idUsr, contrasenya, idLista): None
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

# Igual que ChangeNameListRepUsr, pero el administrador sí que puede cambiar el nombre
# Sintaxis de la función: SetNombreListaRep(idUsr, contrasenya, idLista , nombreLista): None
@csrf_exempt
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCOTRADA
# Si el usuario no le pertenece esa lista y no es administrador y no es una lista 
# pública devuelve FORBIDDEN
# En caso contrario devuelve la privacidad de la lista
# Sintaxis de la función: GetPrivacidadListaRep(idUsr, contrasenya, idLista): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCONTRADA
# Si la lista no es del usuario y no es tipo administrador devuelve FORBIDDEN
# Si privada no es válida devuelve ERROR_LISTA_PRIVACIDAD_INCORRECTA
# En caso contrario cambia la privacidad de la lista
# Sintaxis de la función: SetPrivacidadListaRep(String idUsr, String contrasenya, String idLista, String privada) : int
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la carpeta no existe devuelve ERROR_CARPETA_NO_ENCOTRADA
# Si el usuario no le pertenece esa carpeta y no es administrador y no es una carpeta 
# pública devuelve FORBIDDEN
# En caso contrario devuelve el nombre de la carpeta
# Sintaxis de la función: GetNombreCarpeta(idUsr, contrasenya, idCarpeta): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la carpeta no existe devuelve ERROR_CARPETA_NO_ENCOTRADA
# Si el usuario no le pertenece esa carpeta y no es administrador devuelve FORBIDDEN
# En caso contrario cambia el nombre de la carpeta
# Sintaxis de la función: SetNombreCarpeta(idUsr, contrasenya, idCarpeta, nombreCarpeta): None
@csrf_exempt
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la carpeta no existe devuelve ERROR_CARPETA_NO_ENCOTRADA
# Si el usuario no le pertenece esa carpeta y no es administrador y no es una carpeta 
# pública devuelve FORBIDDEN
# En caso contrario devuelve el nombre de la carpeta
# Sintaxis de la función: GetPrivacidadCarpeta(idUsr, contrasenya, idCarpeta): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la carpeta no existe devuelve ERROR_CARPETA_NO_ENCOTRADA
# Si la privacidad no es válida devuelve ERROR_CARPETA_PRIVACIDAD_NO_VALIDA
# Si el usuario no le pertenece esa carpeta y no es administrador devuelve FORBIDDEN
# En caso contrario cambia el nombre de la carpeta
# Sintaxis de la función: SetPrivacidadCarpeta(idUsr, contrasenya, idCarpeta, privada): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCOTRADO
# Si la contraseña es incorrecta devuelve ERROR_CONTRASENYA_INCORRECTA
# Si la lista no existe devuelve ERROR_LISTA_NO_ENCOTRADA
# Si el usuario no le pertenece esa lista y no es administrador y no es una lista 
# pública devuelve FORBIDDEN
# En caso contrario devuelve el id del usuario al que le pertenece la lista
# Sintaxis de la función: GetUsuarioListaRep(idUsr, contrasenya, idLista): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCONTRADA
# En caso contrario devuelve la imagen del audio
# Sintaxis de la función: GetImagenAudio(idUsr, contrasenya, idAudio): None
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

# Si el usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si el audio no existe devuelve ERROR_CANCION_NO_ENCONTRADA
# En caso contrario guarda la imagen del audio
# Sintaxis de la función: SetImagenAudio(idUsr, contrasenya, idAudio, imagenAudio): None
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


# Devuelve un set con n ids de audios recuperadas mediante una búsqueda global
# (ver definición)
# Sintaxis de la función: GlobalSearch(String query, int n) : Set<String>
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


# Devuelve un set con n ids de audios cuyo nombre contenga alguna de las palabras en # words
# Sintaxis de la función: ByWordSearch(Set<String> query, int n) : Set<String>
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




# Devuelve la id de un audio según el recomendador, de entre todos los audios existentes
# Sintaxis de la función: GetRecomendedAudio(String idUsr, String contrasenya): int idAudio
@csrf_exempt
def GetRecomendedAudio(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)

    idUsr = json_data[constantes.CLAVE_ID_USUARIO]
    passwd = json_data[constantes.CLAVE_CONTRASENYA]

    status = usuarios.ValidateUser(r, idUsr, passwd)
    if (status == False):
        return JsonResponse({'status': status}, status=533)
    
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


# La función entrenar_recomendador no está en la API
@csrf_exempt
def entrenar_recomendador(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Parse the JSON data from the request body to extract idUsuario
    json_data = json.loads(request.body)
    idUsuario = json_data[constantes.CLAVE_ID_USUARIO]
    contrasenya = json_data[constantes.CLAVE_CONTRASENYA]

    status = usuarios.ValidateUser(r, idUsuario, contrasenya)
    if status:
        status = erroresHTTP.OK
    else:
        status = erroresHTTP.ERROR_CONTRASENYA_INCORRECTA
        return JsonResponse({'status': status}, status=status)
    
    if(usuarios.esAdministrador(r, idUsuario) == False):
        return JsonResponse({'error': 'No eres administrador'}, status=erroresHTTP.ERROR_USUARIO_NO_ADMINISTRADOR)
    
    rec.train_model(r, nuevo_modelo=True)

    return JsonResponse({'status': status}, status=status)


# Almacena un ejemplo para entrenar al recomendador
# La valoración será 1 si le ha dado like o al botón de gustar recomendación
# Si no le ha dado a ninguno de los dos botones:
# Cuando se pase a otra canción, la valoración será el porcentaje de la duración que se
# haya escuchado (tiempo escuchado/duracion total)
# Sintaxis de la función: AlmacenarEjemplo(String idUsr, String idAudio, float valoracion): errorHttp
@csrf_exempt
def AlmacenarEjemplo(request):
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
    
    if not moduloAudios.existeCancion(r, idAudio) or not moduloAudios.existePodcast(r, idAudio):
       return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_AUDIO_INEXISTENTE)


    valoracion = float(valoracion)

    gen_datos.store_training_example(r, idUsr, idAudio, valoracion)

    return JsonResponse({'msg': 'Ejemplo almacenado correctamente'}, status=erroresHTTP.OK)


# Devuelve un id del audio dado el link. Si el usuario o el audio no existen, devuelve 0
# Sintaxis de la función: GetValoracion(String idUsr, String idAudio): int valoracion
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


# La función GetValoracionMedia no está en la API
@csrf_exempt
def GetValoracionMedia(request):
    # Compruebo que el método sea GET
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    json_data = json.loads(request.body)
    
    idAudio = json_data[constantes.CLAVE_ID_AUDIO]
    if idAudio == None:
        return JsonResponse({'error': 'Ha ocurrido un problema'}, status=erroresHTTP.ERROR_USUARIO_PARAMETROS_INCORRECTOS)
    
    valoracion = moduloAudios.obtenerValMedia(r, idAudio)

    if valoracion == None:
        valoracion = 0

    return JsonResponse({'valoracion': valoracion}, status=erroresHTTP.OK)


# Almacena la valoración valoracion en el usuario idUsr para el audio idAudio
# Sintaxis de la función: SetValoracion(String idUsr, String idAudio, int valoracion): None
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
    #moduloAudios.cambiarValAudio(r, idAudio, valoracion)

    return JsonResponse({'msg': 'Valoración almacenada correctamente'}, status=erroresHTTP.OK)




# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# En caso contrario manda un email al usuario con el código de recuperación
# y devuelve OK
# Sintaxis de la función: GenerateRandomCodeUsr(email): None
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



# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida para ese usuario devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# calidadPreferida = “alta” o “baja”
# Si todo va bien guarda en la calidad Preferida dado el usuario
# Sintaxis de la función: SetCalidadPorDefectoUsr(idUsr, contrasenya, calidadPreferida): None
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


# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si la contraseña no es válida para ese usuario devuelve 
# ERROR_CONTRASENYA_INCORRECTA
# Si todo va bien devuelve la calidad por defecto del usuario y OK
# Sintaxis de la función: GetCalidadPorDefectoUsr(idUsr, contrasenya): {‘status’ : status, ‘calidad’ : calidad}
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

# Si usuario no existe devuelve ERROR_USUARIO_NO_ENCONTRADO
# Si el codigo de recuperacion es incorrecto devuelve 
# ERROR_USUARIO_CODIGO_RECUPERACION_INCORRECTO
# En caso contrario cambia la contrasenya y devuelve OK
# Sintaxis de la función: RecuperarContrasenya(email, codigo, contrasenya): None
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
