from django.urls import path, re_path
from .views import login, callback, search, refresh_access_token, login_usuario, logout_usuario, crear_usuario, eliminar_usuario, actualizar_usuario
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Documentación de la API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('login/', login, name='login'),
    path('callback', callback, name='callback'),
    path('search/<str:search_type>/<str:q>/', search, name='search'),
    path('refresh-token/', refresh_access_token, name='refresh_token'),

    path('crear_usuario/', crear_usuario, name='crear_usuario'),
    path('login_usuario/', login_usuario, name='login_usuario'),
    path('logout_usuario/', logout_usuario, name='logout_usuario'),
    path('actualizar_usuario/', actualizar_usuario, name='actualizar_usuario'),
    path('eliminar_usuario/', eliminar_usuario, name='eliminar_usuario'),

    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]