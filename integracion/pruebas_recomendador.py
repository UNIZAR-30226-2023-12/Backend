import requests
import json
import base64
from django.middleware import csrf
from django.http import HttpRequest

# URL del endpoint SetSong
url_train = 'http://127.0.0.1:8000/entrenar_recomendador/'
url_add_examples = 'http://127.0.0.1:8000/AlmacenarEjemplo/'

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
    'idUsuario': 'usuario:1',
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
    'idAudio': 'idAudio:10',
    'valoracion': '1'
}


train_data = {
    'idUsr': 'usuario:1',
    'contrasenya': '1234'
}

train_data = json.dumps(train_data)

for i in range(10):
    response = requests.post(url_add_examples, data=params_example) # Pide canciones


# Realizar la petición HTTP POST
response = requests.post(url_train, data=train_data)

# Get the headers from the response
response_headers = response.request.headers

# Convert headers to a string and get its length
headers_size = len(str(response_headers))

# Imprimir el código de estado de la respuesta
print(response.status_code)

# prints de json content
#print(response.json()['nombre'])