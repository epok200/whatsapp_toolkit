from dataclasses import dataclass
from typing import Optional
from functools import wraps
import requests



@dataclass
class HttpResponse:
    status_code: int
    text: str
    json_data: Optional[dict] = None
    
    

def timeout_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.Timeout:
            print("La solicitud ha excedido el tiempo de espera.")
            return HttpResponse(status_code=408, text="Timeout", json_data=None)
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return HttpResponse(
                status_code=500, text="Error", json_data={"error": str(e)}
            )

    return wrapper