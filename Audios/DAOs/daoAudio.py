import redis

# Funcion para guardar una cancion en la base de datos
def guardarCancion(r, id, nombre, artista, calidad, nVeces, val, genero):
    r.hmset(id, {'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'generos': genero})

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