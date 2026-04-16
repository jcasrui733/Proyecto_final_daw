from django.conf import settings
from django.db import models
from django.db.models import Q


class Aula(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "Disponible", "Disponible"
        OCUPADA = "Ocupada", "Ocupada"
        MANTENIMIENTO = "Mantenimiento", "Mantenimiento"

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=80)
    capacidad = models.PositiveIntegerField()
    planta = models.CharField(max_length=10)
    equipamiento = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "aula"
        verbose_name_plural = "aulas"

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        CONFIRMADA = "Confirmada", "Confirmada"
        DENEGADA = "Denegada", "Denegada"
        CANCELADA = "Cancelada", "Cancelada"

    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="reservas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservas")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        ordering = ["-fecha", "hora_inicio"]
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        constraints = [
            models.UniqueConstraint(
                fields=["aula", "usuario", "fecha", "hora_inicio", "hora_fin"],
                name="unique_reserva_usuario_aula_franja",
            )
        ]

    def __str__(self):
        return f"{self.aula} - {self.fecha} {self.hora_inicio}"

    def has_overlap(self):
        """Verifica si hay solape por aula o por usuario con otras reservas activas."""
        active = Reserva.objects.filter(
            fecha=self.fecha,
        ).exclude(estado__in=[self.Estado.DENEGADA, self.Estado.CANCELADA])

        if self.pk:
            active = active.exclude(pk=self.pk)

        return active.filter(
            Q(aula=self.aula, hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio)
            | Q(usuario=self.usuario, hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio)
        ).exists()

    def save(self, *args, **kwargs):
        """Auto-validar reserva al guardar si está en estado Pendiente."""
        if self.estado == self.Estado.PENDIENTE:
            if self.has_overlap():
                self.estado = self.Estado.DENEGADA
            else:
                self.estado = self.Estado.CONFIRMADA
        super().save(*args, **kwargs)


class Incidencia(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = "Baja", "Baja"
        MEDIA = "Media", "Media"
        ALTA = "Alta", "Alta"

    class Estado(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        EN_CURSO = "En curso", "En curso"
        RESUELTA = "Resuelta", "Resuelta"

    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="incidencias")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="incidencias")
    tipo = models.CharField(max_length=120)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "tipo"]
        verbose_name = "incidencia"
        verbose_name_plural = "incidencias"

    def __str__(self):
        return f"{self.tipo} ({self.aula})"


class PerfilUsuario(models.Model):
    class Rol(models.TextChoices):
        PROFESOR = "profesor", "Profesor"
        ADMIN = "admin", "Admin"

    class Estado(models.TextChoices):
        ACTIVO = "Activo", "Activo"
        BLOQUEADO = "Bloqueado", "Bloqueado"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.PROFESOR)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)

    class Meta:
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfiles de usuario"

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_rol_display()})"
