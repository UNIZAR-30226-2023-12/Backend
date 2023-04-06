#########################################################################################
#
#
# FICHERO QUE ALMACENA LOS PREFIJOS Y LAS CLAVES PARA LAS DISTINTAS CLAVES 
# QUE SE PUEDEN NECESITAR
#
#
#########################################################################################

# Fichero de constantes simbólicas
NUMERO_GENEROS = 10


# Constantes simbólicas de las claves de los atributos de usuario
CLAVE_CONTADOR_USUARIOS = "contadorUsuarios"
CLAVE_ID_USUARIO = "idUsuario"
CLAVE_EMAIL = "email"
CLAVE_ALIAS = "alias"
CLAVE_CONTRASENYA = "contrasenya"
CLAVE_TIPO_USUARIO = "tipoUsuario"
CLAVE_ID_ULTIMO_AUDIO = "idUltimoAudio"

# Constantes simbólicas de los prefijos de los sets de usuario
CLAVE_AMIGOS = "amigos"
CLAVE_ARTISTAS = "artistas"
CLAVE_NOTIFICACIONES = "notificaciones"
CLAVE_CARPETAS = "carpetas"
CLAVE_ULTIMOS_AUDIOS = "ultimosAudios"
# Claves para hash de ultimosAudios
CLAVE_SEGUNDOS = "segundos"

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



# Constantes simbólicas para las Carpeta
CLAVE_CONTADOR_CARPETAS = "contadorCarpetas"
CLAVE_ID_CARPETA = "idCarpeta"
CLAVE_NOMBRE_CARPETA = "nombreCarpeta"
CLAVE_PRIVACIDAD_CARPETA = "privacidadCarpeta"
CLAVE_LISTAS_CARPETA = "listasCarpeta"

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
LISTA_TIPO_FAVORTIOS = "listaFavoritos"
LISTA_TIPO_RANKING = "listaRanking"
LISTA_PRIVADA = "privada"
LISTA_PUBLICA = "publica"


# Constantes simbólicas de los prefijos de los sets de listas
CLAVE_AUDIOS = "audios"

CLAVE_HASH_EMAIL_ID = "tablaHashEmailId"