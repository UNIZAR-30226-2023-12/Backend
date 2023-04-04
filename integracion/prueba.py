import requests
import json
import base64
from django.middleware import csrf
from django.http import HttpRequest

# URL del endpoint SetSong
url = 'http://127.0.0.1:8081/SetSong/'

# Crear un objeto HttpRequest vacío
# request = HttpRequest()
# token = csrf.get_token(request)

# Configurar la cabecera HTTP con el token CSRF
# headers = {'X-CSRFToken': token}

# Abrir el archivo MP3 en modo binario
with open('tono_organo.mp3', 'rb') as f:
    # Leer el contenido del archivo
    contenido = f.read()

    # Codificar el contenido en base 64
    codificado = base64.b64encode(contenido)

    # Convertir el resultado a una cadena de texto
    resultado = codificado.decode('utf-8')

# Datos del cuerpo de la petición
data = {
    'nombre': 'Demessieux',
    'artista': 'kdjghd',
    'calidad': 'baja',
    'generos': 'Siglo XX',
    'ficheroBajaCalidad': resultado,
    'longitud': 63
}
json_data = json.dumps(data)

# Realizar la petición HTTP POST
response = requests.post(url, data=json_data)

# Imprimir el código de estado de la respuesta
print(response.status_code)
