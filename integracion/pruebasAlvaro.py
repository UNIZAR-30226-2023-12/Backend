import requests

url = 'http://127.0.0.1:8081/SetUser/'

new_user_data = {
    'idUsr': 'admin',
    'email': 'admin@melodia.es',
    'alias': 'admin',
    'contrasenya': '1234',
    'tipoUsuario': 'admin'
}

response = requests.post(url, json=new_user_data)
print(response.status_code)