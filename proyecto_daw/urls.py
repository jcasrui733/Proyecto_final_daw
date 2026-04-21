from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("api/login/", views.api_login, name="api_login"),
    path("dashboard-profesor/", views.dashboard_profesor, name="dashboard_profesor"),
    path("dashboard-admin/", views.dashboard_admin, name="dashboard_admin"),
    path("buscar-aulas/", views.buscar_aulas, name="buscar_aulas"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("registrar-incidencia/", views.registrar_incidencia, name="registrar_incidencia"),
    path("historial-incidencias/", views.historial_incidencias, name="historial_incidencias"),
    path("gestion-aulas/", views.gestion_aulas, name="gestion_aulas"),
    path("gestion-reservas/", views.gestion_reservas, name="gestion_reservas"),
    path("gestion-incidencias/", views.gestion_incidencias, name="gestion_incidencias"),
    path("gestion-usuarios/", views.gestion_usuarios, name="gestion_usuarios"),
    path('api/register/', views.api_register, name='api_register'),
]
