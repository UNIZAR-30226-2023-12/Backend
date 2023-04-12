import requests
import json
import base64
from django.middleware import csrf
from django.http import HttpRequest

# URL del endpoint SetSong
url = 'http://127.0.0.1:8000/SetUser/'

# Crear un objeto HttpRequest vacío
# request = HttpRequest()
# token = csrf.get_token(request)

# Configurar la cabecera HTTP con el token CSRF
# headers = {'X-CSRFToken': token}
"""
# Abrir el archivo MP3 en modo binario
with open('STARSET-DIE FOR YOU.mp3', 'rb') as f:
    # Leer el contenido del archivo
    contenido = f.read()

    # Codificar el contenido en base 64
    codificado = base64.b64encode(contenido)

    # Convertir el resultado a una cadena de texto
    resultado = codificado.decode('utf-8')

# Datos del cuerpo de la petición
data = {
    'nombre': 'Die for you',
    'idUsuario': '0',
    'contrasenya': '1234',
    'artista': 'Starset',
    'calidad': 'baja',
    'generos': 'Rock',
    'ficheroBajaCalidad': resultado,
    'longitud': 318
}
"""

data = {
    'id': 'Admin',
    'email': 'admin@melodia.es',
    'alias': 'Admin',
    'tipoUsuario': 'admin',
    'contrasenya': '1234',
}

json_data = json.dumps(data)

# Realizar la petición HTTP POST
response = requests.post(url, data=json_data)

# Get the headers from the response
response_headers = response.request.headers

# Convert headers to a string and get its length
headers_size = len(str(response_headers))

# Imprimir el código de estado de la respuesta
print(response.status_code)
print(headers_size)

# prints de json content
#print(response.json()['nombre'])