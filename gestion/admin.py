from django.contrib import admin

from .models import Aula, Incidencia, PerfilUsuario, Reserva


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "capacidad", "planta", "estado")
    search_fields = ("nombre", "tipo", "planta")
    list_filter = ("estado", "planta", "tipo")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("aula", "usuario", "fecha", "hora_inicio", "hora_fin", "estado")
    search_fields = ("aula__nombre", "usuario__username", "motivo")
    list_filter = ("estado", "fecha")


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ("tipo", "aula", "usuario", "prioridad", "estado", "fecha")
    search_fields = ("tipo", "descripcion", "aula__nombre", "usuario__username")
    list_filter = ("estado", "prioridad", "fecha")


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "estado")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    list_filter = ("rol", "estado")
