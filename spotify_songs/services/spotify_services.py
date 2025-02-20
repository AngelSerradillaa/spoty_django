import requests
from django.conf import settings
from django.http import JsonResponse
import time
import random
import string
import urllib
from .token_manage import save_token, load_token

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"
REDIRECT_URL = "http://localhost:8000/api/callback"
CLIENT_ID = "2a71f46595d1477abb92ef7bb7196872"
CLIENT_SECRET = "fb1f6c8dac154237a8851e0e63b661e5"

def get_valid_token(code:str, error:str):

    if error:
        return JsonResponse({'error': 'Se ha producido un error'}, status=400)
    if not code:
       return JsonResponse({'error': 'No se ha retornado codigo de autorización'}, status=400)
    
    token_data = load_token()
    print(token_data)

    if not token_data["access_token"] or not token_data["refresh_token"]or not token_data["expires_in"]:
        print("No hay token se va a realizar el getToken")
        token_data = get_token(code)

    if is_token_expired(token_data):
        print("El token ha expirado, renovando...")
        token_data = refresh_token(token_data["refresh_token"])

    if not token_data:
        return JsonResponse({'error': 'No se pudo obtener el codigo de spotify'}, status=400)
    
    return token_data


def get_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    result = requests.post(SPOTIFY_TOKEN_URL, data=data)

    if result.status_code == 200:
        json_result = result.json()
        access_token = json_result.get("access_token")
        refresh_token = json_result.get("refresh_token")
        expires_in = time.time() + json_result.get("expires_in", 0)

        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "timestamp": time.time()
        }
        print(token_data)
        save_token(token_data)

        return token_data
    else:
        print("Error al obtener el token:", result.status_code, result.content)
        return None

def refresh_token(refresh_token: str):
    """
    Renueva el access_token utilizando el refresh_token.
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    result = requests.post(SPOTIFY_TOKEN_URL, data=data)

    if result.status_code == 200:
        json_result = result.json()

        # Estructura del nuevo token a guardar
        token_data = {
            "access_token": json_result["access_token"],
            "refresh_token": refresh_token,  # El refresh_token no cambia
            "expires_in": json_result["expires_in"],
            "timestamp": time.time()
        }
        print(token_data)
        save_token(token_data)

        return token_data
    else:
        print("Error al renovar el token:", result.status_code, result.content)
        return None

def is_token_expired(token_data):
    """
    Verifica si el token ha expirado comparando el tiempo actual con el timestamp.
    """
    current_time = time.time()
    if token_data["expires_in"] is None or token_data["timestamp"] is None:
        return True 

    expires_in = token_data["expires_in"]
    timestamp = token_data["timestamp"]

    return current_time > (timestamp + expires_in)

def generar_string_aleatorio():
    caracteres = string.ascii_letters + string.digits  # Letras (a-z, A-Z) y números (0-9)
    return ''.join(random.choice(caracteres) for _ in range(16))

def get_auth_url():
    state = generar_string_aleatorio()
    scope = "user-read-private user-read-email"
    print(f"CLIENT_ID: {CLIENT_ID}")

    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URL,
        'scope': scope,
        'state': state
    }

    return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"