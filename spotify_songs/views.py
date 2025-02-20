from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from .services.spotify_services import get_auth_url, get_valid_token, refresh_token, load_token, refresh_token, is_token_expired
from .services.search_manage import save_search_results
from .services.users_manage import get_logged_user, load_users, save_users, save_logged_user
import requests
from .models import User, Token, Artist, Song
from passlib.context import CryptContext
import webbrowser

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def login(request):
    auth_url = get_auth_url()
    print(auth_url)
    try:
        print("Hola")
        return webbrowser.open(auth_url)
    except Exception as e:
        # Si ocurre un error, devolver un mensaje en formato JSON con el error
        print(f"Error al generar o redirigir a la URL de autenticación: {str(e)}")
        return JsonResponse({'error': 'Hubo un problema al redirigir a la URL de autenticación.'}, status=500)

def callback(request):
    code = request.GET.get('code')
    error = request.GET.get('error')
    print("Se ha ejecutado callback")

    if error:
        return JsonResponse({'error': 'Se ha producido un error'}, status=400)
    if not code:
        return JsonResponse({'error': 'No se ha retornado código de autorización'}, status=400)
    
    token_data = get_valid_token(code, error)

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data["expires_in"]

    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    print(f"Expires In: {expires_in}")

    html_content = f"""
        <html>
            <body>
                <h1>El token ha sido almacenado correctamente.</h1>
                <p>Access Token: {access_token}</p>
                <p>Refresh Token: {refresh_token}</p>
                <p>Expires In: {expires_in}</p>
                <p>Puedes ir a la documentación para probar los endpoints <a href="/api/redoc/">aquí</a>.</p>
            </body>
        </html>
    """
    
    return HttpResponse(html_content, content_type="text/html")

@csrf_exempt
def search(request, q, search_type):
    #data = json.loads(request.body)
    #query = data.get('q')
    #search_type = data.get('type')
    print(q, search_type)
    if not q or not search_type:
        print("Hola")
        return JsonResponse({'error': 'No hay query de búsqueda'}, status=400)
    

    token_data = load_token()
    if is_token_expired(token_data):
        print("El token ha expirado, renovando...")
        token_data = refresh_token(token_data["refresh_token"])

    access_token = token_data["access_token"]
    url = f"https://api.spotify.com/v1/search?q={q}&type={search_type}&limit=10"
    print(url)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        results = response.json()

        # Guardar los resultados en un archivo JSON específico para el usuario
        user = get_logged_user()
        save_search_results(user, search_type, q, results)

        return JsonResponse(results)
    else:
        print(f"Error al buscar en Spotify: {response.status_code}, {response.content}")
        return None
    

#def user_profile(request):
#    user_info = manage_user()
#    user, created = User.objects.get_or_create(user=user_info['id'])
#    return JsonResponse(user_info)

def refresh_access_token(request):
    new_token = refresh_token()
    return JsonResponse(new_token)

@csrf_exempt
def crear_usuario(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('user')
        password = data.get('password')
        full_name = data.get('full_name')

        users = load_users()
        if not username or not password or not full_name:
            return JsonResponse({'error': f"Falta el usuario: {username}, la contraseña: {password} o el nombre completo: {full_name}"}, status=400)
        
        if username in users:
            return JsonResponse({'error': 'El usuario ya existe'}, status=400)
        
        #hashed_password = pwd_context.hash(password)
        users[username] = {"password": password, "full_name": full_name}
        save_users(users)
        return JsonResponse({'message': f"Usuario {username} creado exitosamente"})
    
@csrf_exempt
def login_usuario(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('user')
        password = data.get('password')

        users = load_users()

        if username not in users:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        stored_user = users[username]
        #if not pwd_context.verify(password, stored_user["password"]):
        #    return JsonResponse({'error': 'Contraseña incorrecta'}, status=404)
        save_logged_user(username)
        return HttpResponseRedirect("http://127.0.0.1:8000/api/login")
        

@csrf_exempt
def logout_usuario(request):
    return JsonResponse({'message': 'Logged out successfully'})

@csrf_exempt
def actualizar_usuario(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        username = data.get('user')
        new_password = data.get('new_password')
        full_name = data.get('full_name')

        users = load_users()

        if username not in users:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        #hashed_password = pwd_context.hash(new_password)
        users[username] = {"password": new_password, "full_name": full_name}
        save_users(users)
        return {"message": f"Usuario {username} actualizado exitosamente"}

@csrf_exempt
def eliminar_usuario(request):
    if request.method == 'DELETE':
        data = json.loads(request.body)
        username = data.get('user')

        users = load_users()
        
        if username not in users:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        del users[username]
        save_users(users)
        return {"message": f"Usuario {username} eliminado exitosamente"}
