from .models import ModelUser
from .precio_dolar import dollar
import json 

def json_serializer(request):
    CreditosAll = request.user.CreditosTotales
    PrecioDollarContex = dollar(request)
    PrecioDollar = PrecioDollarContex['dollar']
    lista = [{'id': 1, 'CreditosTotales': CreditosAll, 'PrecioDolar': f'MXN {PrecioDollar}'}]
    
    serializado = json.dumps(lista)
    
    return json.loads(serializado)