import redis

# Funcion para guardar una cancion en la base de datos
def guardarCancion(r, id, nombre, artista, calidad, nVeces, val, genero):
    r.hmset(id, {'nombre': nombre, 'artista': artista, 'calidad': calidad, 'nVeces': nVeces, 'val': val, 'generos': genero})

