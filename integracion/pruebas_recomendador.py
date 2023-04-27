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
url_get_song = 'http://'+ip+':'+port+'/GetSong/'

url_train = 'http://'+ip+':'+port+'/entrenar_recomendador/'
url_add_examples = 'http://'+ip+':'+port+'/AlmacenarEjemplo/'
url_recomend_song = 'http://'+ip+':'+port+'/GetRecomendedAudio/'

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

new_user = {
    'idUsr': 'admin',
    'contrasenya': '1234',
    'alias': 'admin',
    'email': 'admin@melodia.es',
    'tipoUsuario': 'admin'
}

params_example = {
    'idUsr': 'usuario:1',
    'idAudio': 'idAudio:1',
    'valoracion': '1'
}

get_audio_params = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234',
    'idAudio': 'idAudio:1'
}


train_data = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

examples = [
{
    'idUsr': 'usuario:1',
    'idAudio': 'idAudio:1',
    'valoracion': '1'
},
]

new_user = json.dumps(new_user)
new_song_data = json.dumps(new_song_data)
get_audio_params = json.dumps(get_audio_params)
train_data = json.dumps(train_data)

#response = requests.post(url_set_usr, data=new_user) # Añade ejemplos de entrenamiento
#print("set user: ", response.status_code)

#response = requests.post(url_set_song, data=new_song_data) # Añade ejemplos de entrenamiento
#print("set song: ", response.status_code)

for i in range(1000):
    response = requests.post(url_add_examples, data=params_example) # Añade ejemplos de entrenamiento

# Realizar la petición HTTP POST
response = requests.post(url_train, data=train_data)    # Entrena al recomendador


for i in range(100):
    response = requests.get(url_get_song, data=get_audio_params) # Genera un estado de sesión del usuario

response = requests.post(url_recomend_song, data=train_data) # Obtiene una canción recomendada


# Get the headers from the response
response_headers = response.request.headers

# Convert headers to a string and get its length
headers_size = len(str(response_headers))

# Imprimir el código de estado de la respuesta
print(response.status_code)

# prints de json content
#print(response.json()['nombre'])