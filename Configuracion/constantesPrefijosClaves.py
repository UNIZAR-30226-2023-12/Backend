#########################################################################################
#
#
# FICHERO QUE ALMACENA LOS PREFIJOS Y LAS CLAVES PARA LAS DISTINTAS CLAVES 
# QUE SE PUEDEN NECESITAR
#
#
#########################################################################################

# Fichero de constantes simbólicas
GENERO_POP = 0
GENERO_ROCK = 1
GENERO_METAL = 2
GENERO_RAP = 3
GENERO_REGGAE = 4
GENERO_JAZZ = 5
GENERO_BLUES = 6
GENERO_CLASICA = 7
GENERO_ELECTRONICA = 8
GENERO_FOLK = 9
GENERO_LATINA = 10
GENERO_INDIE = 11
GENERO_COUNTRY = 12
GENERO_AMBIENT = 13
GENERO_TRAP = 14
GENERO_DANCE = 15
GENERO_HIPHOP = 16
GENERO_RNB = 17
GENERO_SOUL = 18
GENERO_PUNK = 19
GENERO_FUNK = 20

GENERO_NUMERO_GENEROS = 21

def obtenerIDGenero(genero):
    genero = genero.lower()

    if(genero == "pop"):
        return GENERO_POP
    elif(genero == "rock"):
        return GENERO_ROCK
    elif(genero == "metal"):
        return GENERO_METAL
    elif(genero == "rap"):
        return GENERO_RAP
    elif(genero == "reggae"):
        return GENERO_REGGAE
    elif(genero == "jazz"):
        return GENERO_JAZZ
    elif(genero == "blues"):
        return GENERO_BLUES
    elif(genero == "clasica"):
        return GENERO_CLASICA
    elif(genero == "electronica"):
        return GENERO_ELECTRONICA
    elif(genero == "folk"):
        return GENERO_FOLK
    elif(genero == "latina"):
        return GENERO_LATINA
    elif(genero == "indie"):
        return GENERO_INDIE
    elif(genero == "country"):
        return GENERO_COUNTRY
    elif(genero == "ambient"):
        return GENERO_AMBIENT
    elif(genero == "trap"):
        return GENERO_TRAP
    elif(genero == "dance"):
        return GENERO_DANCE
    elif(genero == "hiphop"):
        return GENERO_HIPHOP
    elif(genero == "rnb"):
        return GENERO_RNB
    elif(genero == "soul"):
        return GENERO_SOUL
    elif(genero == "punk"):
        return GENERO_PUNK
    elif(genero == "funk"):
        return GENERO_FUNK
    else:
        return -1
    

def obtenerNombreGenero(genero):

    if(genero == GENERO_POP):
        return "pop"
    elif(genero == GENERO_ROCK):
        return "rock"
    elif(genero == GENERO_METAL):
        return "metal"
    elif(genero == GENERO_RAP):
        return "rap"
    elif(genero == GENERO_REGGAE):
        return "reggae"
    elif(genero == GENERO_JAZZ):
        return "jazz"
    elif(genero == GENERO_BLUES):
        return "blues"
    elif(genero == GENERO_CLASICA):
        return "clasica"
    elif(genero == GENERO_ELECTRONICA):
        return "electronica"
    elif(genero == GENERO_FOLK):
        return "folk"
    elif(genero == GENERO_LATINA):
        return "latina"
    elif(genero == GENERO_INDIE):
        return "indie"
    elif(genero == GENERO_COUNTRY):
        return "country"
    elif(genero == GENERO_AMBIENT):
        return "ambient"
    elif(genero == GENERO_TRAP):
        return "trap"
    elif(genero == GENERO_DANCE):
        return "dance"
    elif(genero == GENERO_HIPHOP):
        return "hiphop"
    elif(genero == GENERO_RNB):
        return "rnb"
    elif(genero == GENERO_SOUL):
        return "soul"
    elif(genero == GENERO_PUNK):
        return "punk"
    elif(genero == GENERO_FUNK):
        return "funk"
    else:
        return ""

    
    




RECOMENDADOR_TAMANYO_VENTANA_PREDICCION = 10

# Sets globales
PREFIJO_LISTA_GLOBAL_CANCIONES = "listaGlobalCanciones"
PREFIJO_LISTA_GLOBAL_USUARIOS = "listaGlobalUsuarios"
PREFIJO_LISTA_GLOBAL_ARTISTAS = "listaGlobalArtistas"
PREFIJO_LISTA_GLOBAL_PODCASTS = "listaGlobalPodcasts"

# Constantes simbólicas de las claves de los atributos de usuario
CLAVE_CONTADOR_USUARIOS = "contadorUsuarios"
CLAVE_ID_USUARIO = "idUsr"
CLAVE_EMAIL = "email"
CLAVE_ALIAS = "alias"
CLAVE_CONTRASENYA = "contrasenya"
CLAVE_TIPO_USUARIO = "tipoUsuario"
CLAVE_ID_ULTIMO_AUDIO = "idUltimoAudio"
CLAVE_IMAGEN_PERFIL = "imagenPerfil"
CLAVE_QUERY = "query"
CLAVE_N = "n"
CLAVE_TEMPORAL_ENTRENAMIENTO = "datos_temporales"
CLAVE_CALIDAD_PREFERIDA = "calidadPreferida"

CLAVE_ID_AMIGO = "idAmigo"

# Prefijos de las claves relacionadas con los usuarios
PREFIJO_ID_USUARIO = "usuario"
PREFIJO_AMIGOS = "amigos"
PREFIJO_ARTISTAS_SUSCRITOS = "artistas"
PREFIJO_NOTIFICACIONES = "notificaciones"
PREFIJO_CARPETAS = "carpetas"
PREFIJO_SEGUNDOS_AUDIOS = "segundosAudios"
# Claves para hash de ultimosAudios

# Clave de set de ids de administradores
CLAVE_ADMINISTRADORES = "administradores"
# Se usa tambien para acceder al set de listas de Carpeta
CLAVE_LISTAS = "listas"
# Se usa para acceder a las canciones de un artista
CLAVE_CANCIONES = "canciones"

# Constantes simbólicas de los tipos de usuario
USUARIO_ADMINISTRADOR = "admin"
USUARIO_NORMAL = "normalUser"
USUARIO_ARTISTA = "artista"

# Constantes simbólicas para los audios
CLAVE_ID_AUDIO = "idAudio"
CLAVE_NOMBRE_AUDIO = "nombre"
CLAVE_GENEROS_AUDIO = "generos"
CLAVE_DESCRIPCION_AUDIO = "desc"
CLAVE_ARTISTA_AUDIO = "artista"
CLAVE_VALORACION_AUDIO = "val"
CLAVE_NUMERO_REPRODUCCIONES = "nVeces"
CLAVE_CALIDAD_AUDIO = "calidad"
CLAVE_FICHERO_ALTA_CALIDAD = "ficheroAltaCalidad"
CLAVE_FICHERO_BAJA_CALIDAD = "ficheroBajaCalidad"
CLAVE_PREFIJO_AUDIO = "audio"
CLAVE_ES_PODCAST = "esPodcast"
CLAVE_SECONDS = "second"
CLAVE_IMAGEN_AUDIO = "imagenAudio"
CLAVE_LINK_AUDIO = "linkAudio"
CLAVE_VALORACION = "valoracion"


CLAVE_DEFAULT_AUDIO_IMAGE = "defaultAudioImage"

CLAVE_DEFAULT_USER_IMAGE = 'defaultUserImage'






# Constantes simbólicas para las Carpeta
CLAVE_CONTADOR_CARPETAS = "contadorCarpetas"
CLAVE_ID_CARPETA = "idCarpeta"
CLAVE_NOMBRE_CARPETA = "nombreCarpeta"
CLAVE_PRIVACIDAD_CARPETA = "privacidadCarpeta"
CLAVE_LISTAS_CARPETA = "listasCarpeta"
PREFIJO_ID_CARPETA = "carpeta"
CARPETA_PUBLICA = "publica"
CARPETA_PRIVADA = "privada"

# Constantes simbólicas para los prefijos de los sets de carpeta

# Constantes simbólicas para las Notificaciones
CLAVE_CONTADOR_NOTIFICACIONES = "contadorNotificaciones"
CLAVE_ID_NOTIFICACION = "idNotificacion"
CLAVE_TIPO_NOTIFICACION = "tipoNotificacion"
CLAVE_ID_USUARIO_EMISIOR = "idUsuarioEmisor"
CLAVE_TITULO_NOTIFICACION = "titulo"
CLAVE_MENSAJE_NOTIFICACION = "mensaje"
NOTIFCACION_TIPO_NORMAL = "normal"
NOTIFICACION_TIPO_AMIGO = "amigo"
NOTIFICACION_TIPO_SOLICITUD_ARTISTA = "quieroArtista"

PREFIJO_ID_NOTIFICACION = "notificacion"

# Constantes para mensajes y títulos default
TITULO_NOTIFICACION_ARTISTA = "Solicitud de artista"
MENSAJE_NOTIFICACION_ARTISTA = " quiere ser artista"

# Constantes simbólicas para las Lista de reproducción
CLAVE_CONTADOR_LISTAS = "contadorListas"
CLAVE_ID_LISTA = "idLista"
CLAVE_NOMBRE_LISTA = "nombreLista"
CLAVE_PRIVACIDAD_LISTA = "privada"
CLAVE_TIPO_LISTA = "tipoLista"
LISTA_TIPO_REPRODUCCION = "listaReproduccion"
LISTA_TIPO_FAVORITOS = "listaFavoritos"
LISTA_TIPO_RANKING = "listaRanking"
LISTA_PRIVADA = "privada"
LISTA_PUBLICA = "publica"


# Constantes simbólicas de los prefijos de los sets de listas
PREFIJO_ID_LISTA = "lista"
CLAVE_AUDIOS = "audios"

CLAVE_HASH_EMAIL_ID = "tablaHashEmailId"


CLAVE_SET_USUARIOS_ENTRENADOS = "usuariosEntrenados"
CLAVE_LISTA_ENTRENAMIENTO = "listaEntrenamiento"
PREFIJO_SEGUNDOS_REPRODUCIDOS_AUDIO = "segundosReproducidos"

CLAVE_DIA = "dia"



CLAVE_ID_ERROR = "idError"

CORREO_RECUPERACION = "enterprisemussa@gmail.com"
CONTRASENYA_CORREO_RECUPERACION = "jrbecurardgvnxxw"
PREFIJO_CODIGO_RECUPERACION = "codigo"
CLAVE_CODIGO_RECUPERACION = "codigo"
