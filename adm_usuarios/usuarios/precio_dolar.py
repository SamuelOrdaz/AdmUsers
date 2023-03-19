import requests
import json
#Función para obtener precio del dolar
def dollar(request):
    url = 'https://api.exchangerate.host/latest?base=USD&symbols=MXN'
    response = requests.get(url)
    data = response.json()
    valor = data["rates"]["MXN"]
    return {'dollar':valor}