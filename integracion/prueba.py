import requests
import json
import base64
from django.middleware import csrf
from django.http import HttpRequest

ip = '127.0.0.1'
port = '8000'

# URL del endpoint SetSong
url_set_song = 'http://'+ip+':'+port+'/SetSong/'
url_set_usr = 'http://'+ip+':'+port+'/SetUser/'
url_get_usr = 'http://'+ip+':'+port+'/GetUser/'
url_get = 'http://'+ip+':'+port+'/GetSong/'
url_busqueda = 'http://'+ip+':'+port+'/GlobalSearch/'

# Crear un objeto HttpRequest vacío
# request = HttpRequest()
# token = csrf.get_token(request)

# Configurar la cabecera HTTP con el token CSRF
# headers = {'X-CSRFToken': token}

# Abrir el archivo MP3 en modo binario
with open('STARSET-DIE FOR YOU.mp3', 'rb') as f:
    # Leer el contenido del archivo
    contenido = f.read()

    # Codificar el contenido en base 64
    codificado = base64.b64encode(contenido)

    # Convertir el resultado a una cadena de texto
    resultado = codificado.decode('utf-8')

# String idUsr, String email, String alias, String contrasenya, String tipoUsuario
new_user_data = {
    'idUsr': 'admin',
    'email': 'admin@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin'
}

# Datos del cuerpo de la petición
new_song_data = {
    'nombre': 'Die for you',
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'artista': 'Starset',
    'calidad': 'baja',
    'generos': 'Rock',
    'esPodcast': 'False',
    'ficheroBajaCalidad': "",
    'longitud': 318
}

params_example = {
    'idUsr': 'usuario:1',
    'idSong': 'idAudio:1',
    'calidadAlta': 'True',
    'esCancion': 'True'
}

params_get_usr = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}



# Realizar la petición HTTP POST
response = requests.post(url_set_song, json=new_song_data)
response = requests.get(url_get, params=params_get_song)
usr = requests.get(url_get_usr, params=params_get_usr)

search = requests.get(url_busqueda, params={'query': 'Die for you'})

print(search.json())


# Get the headers from the response
response_headers = response.request.headers

# Convert headers to a string and get its length
headers_size = len(str(response_headers))

# Imprimir el código de estado de la respuesta
print(response.status_code)
print(response.json())
# prints de json content
#print(response.json()['nombre'])