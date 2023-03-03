import redis


#########################################################################################
#
#
# FUNCIONES PARA ALMACENAR/ACTUALIZAR CANCIONES
#
#
#########################################################################################

# Funcion para guardar una cancion en la base de datos
def guardarCancion(r, id, nombre, artista, calidad, nVeces, val, genero):
    r.hmset(id, {'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'generos': genero})

# Funcion para cambiar el nombre de una cancion
def cambiarNombreCancion(r, id, nombre):
    r.hset(id, 'nombre', nombre)

# Funcion para cambiar el artista de una cancion
def cambiarArtistaCancion(r, id, artista):
    r.hset(id, 'artista', artista)

# Funcion para cambiar la calidad de una cancion
def cambiarCalidadCancion(r, id, calidad):
    r.hset(id, 'calidad', calidad)

# Funcion para cambiar el num de veces que se ha escuchado una cancion
def cambiarVecesreproducidasCancion(r, id, nVeces):
    r.hset(id, 'nVeces', nVeces)

# Funcion para cambiar la valoracion de una cancion
def cambiarValCancion(r, id, val):
    r.hset(id, 'val', val)

# Funcion para cambiar el genero de una cancion
def cambiarGeneroCancion(r, id, genero):
    r.hset(id, 'generos', genero)

#########################################################################################
#
#
# FUNCIONES PARA OBTENER CANCIONES Y SUS ATRIBUTOS POR SEPARADO
#
#
#########################################################################################

# Funcion para obtener una cancion
def obtenerCancion(r, id):
    return r.hgetall(id)

# Funcion para obtener el num de veces que se ha escuchado una cancion
def obtenerVecesreproducidasCancion(r, id):
    return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de una cancion
def obtenerValCancion(r, id):
    return r.hget(id, 'val')

# Funcion para obtener el genero de una cancion
def obtenerGeneroCancion(r, id):
    return r.hget(id, 'generos')

# Funcion para obtener el nombre de una cancion
def obtenerNombreCancion(r, id):
    return r.hget(id, 'nombre')

# Funcion para obtener el artista de una cancion
def obtenerArtistaCancion(r, id):
    return r.hget(id, 'artista')

# Funcion para obtener la calidad de una cancion
def obtenerCalidad(r, id):
    return r.hget(id, 'calidad')

#########################################################################################
#
#
# FUNCIONES PARA ALMACENAR/ACTUALIZAR PODCASTS
#
#
#########################################################################################

# Funcion para guardar un podcast en la base de datos
def guardarPodcast(r, id, nombre, artista, calidad, nVeces, val, desc):
    r.hmset(id, {'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'desc': desc})

# Funcion para cambiar el nombre de un podcast
def cambiarNombrePodcast(r, id, nombre):
    r.hset(id, 'nombre', nombre)

# Funcion para cambiar el artista de un podcast
def cambiarArtistaPodcast(r, id, artista):
    r.hset(id, 'artista', artista)

# Funcion para cambiar la calidad de un podcast
def cambiarCalidadPodcast(r, id, calidad):
    r.hset(id, 'calidad', calidad)

# Funcion para cambiar el num de veces que se ha escuchado un podcast
def cambiarVecesreproducidasPodcast(r, id, nVeces):
    r.hset(id, 'nVeces', nVeces)

# Funcion para cambiar la valoracion de un podcast
def cambiarValPodcast(r, id, val):
    r.hset(id, 'val', val)

# Funcion para cambiar la descripcion de un podcast
def cambiarDescPodcast(r, id, desc):
    r.hset(id, 'desc', desc)

#########################################################################################
#
#
# FUNCIONES PARA OBTENER PODCASTS Y SUS ATRIBUTOS POR SEPARADO
#
#
#########################################################################################

# Funcion para obtener un podcast
def obtenerPodcast(r, id):
    return r.hgetall(id)

# Funcion para obtener el nombre de un podcast
def obtenerNombrePodcast(r, id):
    return r.hget(id, 'nombre')

# Funcion para obtener el artista de un podcast
def obtenerArtistaPodcast(r, id):
    return r.hget(id, 'artista')

# Funcion para obtener la calidad de un podcast
def obtenerCalidadPodcast(r, id):
    return r.hget(id, 'calidad')

# Funcion para obtener el num de veces que se ha escuchado un podcast
def obtenerVecesreproducidasPodcast(r, id):
    return r.hget(id, 'nVeces')

# Funcion para obtener la valoracion de un podcast
def obtenerValPodcast(r, id):
    return r.hget(id, 'val')

# Funcion para obtener la descripcion de un podcast
def obtenerDescPodcast(r, id):
    return r.hget(id, 'desc')

#########################################################################################
#
#
# FUNCIONES PARA GESTIONAR EL CREADO/MODIFICACION DE PLAYLISTS
#
#
#########################################################################################

# Funcion para crear una playlist
def crearPlaylist(r, id, nombre, usuario, idListaIDsCanciones, canciones, podcasts, publica):
    # Primero creo la playlist con sus datos
    r.hmset(id, {'nombre': nombre, 'usuario': usuario, 'idListaIDsCanciones': idListaIDsCanciones, 'publica': publica})

    # Creo la lista de canciones y podcasts
    r.sadd(idListaIDsCanciones, *canciones)
    r.sadd(idListaIDsCanciones, *podcasts)

# Funcion para cambiar el nombre de una playlist
def cambiarNombrePlaylist(r, id, nombre):
    r.hset(id, 'nombre', nombre)

# Funcion para cambiar el usuario de una playlist
def cambiarUsuarioPlaylist(r, id, usuario):
    r.hset(id, 'usuario', usuario)

# Funcion para cambiar el tipo de playlist (publica o privada)
def cambiarPublicaPlaylist(r, id, publica):
    r.hset(id, 'publica', publica)

# Funcion para añadir una o más canciones a una playlist
def anadirCancionPlaylist(r, idLista, idCanciones):
    # Primero obtengo la lista de canciones de la playlist
    idListaCan = r.hget(idLista, 'idListaIDsCanciones')

    # Añado las canciones a la lista
    r.sadd(idListaCan, *idCanciones)

# Funcion para añadir un o más podcasts a una playlist
def anadirPodcastPlaylist(r, idLista, idPodcasts):
    # Primero obtengo la lista de podcasts de la playlist
    idListaPod = r.hget(idLista, 'idListaIDsCanciones')

    # Añado los podcasts a la lista
    r.sadd(idListaPod, *idPodcasts)
    