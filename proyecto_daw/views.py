from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.urls import reverse

from gestion.models import Aula, Incidencia, PerfilUsuario, Reserva


def seed_demo_data():
    aulas = [
        {"nombre": "Aula 101", "tipo": "Aula normal", "capacidad": 30, "planta": "1ª", "estado": "Disponible"},
        {"nombre": "Laboratorio Informática 2", "tipo": "Laboratorio", "capacidad": 20, "planta": "2ª", "estado": "Disponible"},
        {"nombre": "Aula de Música", "tipo": "Especializada", "capacidad": 25, "planta": "1ª", "estado": "Ocupada"},
        {"nombre": "Biblioteca", "tipo": "Zona común", "capacidad": 50, "planta": "0ª", "estado": "Disponible"},
    ]

    for aula_data in aulas:
        Aula.objects.get_or_create(
            nombre=aula_data["nombre"],
            defaults={
                "tipo": aula_data["tipo"],
                "capacidad": aula_data["capacidad"],
                "planta": aula_data["planta"],
                "estado": aula_data["estado"],
                "equipamiento": "",
            },
        )

    users = [
        {"nombre": "Laura García", "email": "laura@instituto.es", "password": "123456", "rol": "profesor", "estado": "Activo"},
        {"nombre": "Marta Ruiz", "email": "marta@instituto.es", "password": "123456", "rol": "profesor", "estado": "Activo"},
        {"nombre": "Admin Centro", "email": "admin@instituto.es", "password": "123456", "rol": "admin", "estado": "Activo"},
    ]

    for user_data in users:
        user, created = User.objects.get_or_create(
            username=user_data["email"],
            defaults={
                "email": user_data["email"],
                "first_name": user_data["nombre"].split(" ", 1)[0],
                "last_name": user_data["nombre"].split(" ", 1)[1] if " " in user_data["nombre"] else "",
            },
        )
        if created:
            user.set_password(user_data["password"])
            user.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        perfil.rol = user_data["rol"]
        perfil.estado = user_data["estado"]
        perfil.save()

    laura = User.objects.filter(username="laura@instituto.es").first()
    admin = User.objects.filter(username="admin@instituto.es").first()
    aula_101 = Aula.objects.filter(nombre="Aula 101").first()
    aula_laboratorio = Aula.objects.filter(nombre="Laboratorio Informática 2").first()

    if laura and aula_101:
        Reserva.objects.get_or_create(
            aula=aula_101,
            usuario=laura,
            fecha="2026-04-10",
            hora_inicio="10:00",
            hora_fin="11:00",
            defaults={
                "motivo": "Reunión de tutoría",
                "estado": "Confirmada",
            },
        )

    if laura and aula_laboratorio:
        Reserva.objects.get_or_create(
            aula=aula_laboratorio,
            usuario=laura,
            fecha="2026-04-11",
            hora_inicio="12:00",
            hora_fin="13:00",
            defaults={
                "motivo": "Clase práctica",
                "estado": "Pendiente",
            },
        )

    if laura and aula_101:
        if not Incidencia.objects.filter(aula=aula_101, usuario=laura, tipo="Proyector averiado").exists():
            Incidencia.objects.create(
                aula=aula_101,
                usuario=laura,
                tipo="Proyector averiado",
                prioridad="Alta",
                descripcion="El proyector no enciende.",
                estado="Pendiente",
            )

    if laura and aula_laboratorio:
        if not Incidencia.objects.filter(aula=aula_laboratorio, usuario=laura, tipo="Ordenador no funciona").exists():
            Incidencia.objects.create(
                aula=aula_laboratorio,
                usuario=laura,
                tipo="Ordenador no funciona",
                prioridad="Media",
                descripcion="Un equipo no arranca correctamente.",
                estado="En curso",
            )


def get_user_email_from_request(request):
    email = (request.POST.get("user_email") or request.GET.get("user_email") or "").strip().lower()
    return email


def require_admin_role(request):
    """Check if user is logged in and has admin role. Returns (is_admin, user_email)."""
    user_email = get_user_email_from_request(request)
    if not user_email:
        return False, None
    user = User.objects.filter(email__iexact=user_email).select_related("perfil").first()
    if not user:
        return False, user_email

    try:
        perfil = user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = None

    if (user.is_staff or user.is_superuser) and perfil is None:
        perfil = PerfilUsuario.objects.create(user=user, rol="admin", estado="Activo")
    elif (user.is_staff or user.is_superuser) and perfil.rol != "admin":
        perfil.rol = "admin"
        perfil.save(update_fields=["rol"])

    if not perfil or perfil.rol != "admin":
        return False, user_email
    return True, user_email


def admin_redirect(view_name, user_email):
    url = reverse(view_name)
    if user_email:
        return f"{url}?user_email={user_email}"
    return url


def full_name(user):
    name = user.get_full_name().strip()
    return name or user.username


def parse_full_name(value):
    parts = value.strip().split(None, 1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def parse_tramo(horario):
    if "-" not in (horario or ""):
        return None, None

    start_text, end_text = [part.strip() for part in horario.split("-", 1)]
    try:
        start_time = datetime.strptime(start_text, "%H:%M").time()
        end_time = datetime.strptime(end_text, "%H:%M").time()
    except ValueError:
        return None, None

    if start_time >= end_time:
        return None, None

    return start_time, end_time


def index(request):
    return render(request, "index.html")


def api_login(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Metodo no permitido."}, status=405)

    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    if not email or not password:
        return JsonResponse({"ok": False, "message": "Email y contraseña son obligatorios."}, status=400)

    user = authenticate(request, username=email, password=password)
    if not user:
        return JsonResponse({"ok": False, "message": "Email o contraseña incorrectos."}, status=401)

    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    if (user.is_staff or user.is_superuser) and perfil.rol != "admin":
        perfil.rol = "admin"
        perfil.save(update_fields=["rol"])
    if perfil.estado == "Bloqueado":
        return JsonResponse({"ok": False, "message": "Usuario bloqueado. Contacta con administración."}, status=403)

    nombre = user.get_full_name().strip() or user.username
    return JsonResponse(
        {
            "ok": True,
            "user": {
                "id": user.id,
                "nombre": nombre,
                "email": user.email or user.username,
                "rol": perfil.rol,
                "estado": perfil.estado,
            },
        }
    )


def dashboard_profesor(request):
    user_email = get_user_email_from_request(request)
    user = User.objects.filter(email__iexact=user_email).first() if user_email else None

    reservas_usuario = Reserva.objects.none()
    incidencias_usuario = Incidencia.objects.none()
    nombre_usuario = ""

    if user:
        reservas_usuario = Reserva.objects.select_related("aula").filter(usuario=user)
        incidencias_usuario = Incidencia.objects.select_related("aula").filter(usuario=user)
        nombre_usuario = full_name(user)

    hoy = timezone.localdate()
    proximas_reservas = reservas_usuario.exclude(estado__in=["Cancelada", "Denegada"]).filter(fecha__gte=hoy).order_by("fecha", "hora_inicio")[:5]
    incidencias_recientes = incidencias_usuario.order_by("-fecha")[:5]

    context = {
        "user_email": user_email,
        "nombre_usuario": nombre_usuario,
        "total_reservas": reservas_usuario.count(),
        "total_incidencias_pendientes": incidencias_usuario.filter(estado="Pendiente").count(),
        "aulas_disponibles": Aula.objects.filter(estado="Disponible").count(),
        "proximas_reservas": proximas_reservas,
        "incidencias_recientes": incidencias_recientes,
    }
    return render(request, "dashboard_profesor.html", context)


def dashboard_admin(request):
    return render(request, "dashboard_admin.html", {"user_email": get_user_email_from_request(request)})


def buscar_aulas(request):
    selected_date = request.POST.get("fecha") or request.GET.get("fecha") or "2026-04-10"
    selected_tramo = request.POST.get("horario") or request.GET.get("horario") or "10:00 - 12:00"

    if request.method == "POST":
        user_email = get_user_email_from_request(request)
        aula_id = request.POST.get("aula_id")
        if not user_email:
            messages.error(request, "No se ha podido identificar el usuario.")
        else:
            user = User.objects.filter(email__iexact=user_email).select_related("perfil").first()
            aula = Aula.objects.filter(pk=aula_id).first()

            if not user or not aula:
                messages.error(request, "No se ha podido crear la reserva.")
            else:
                hora_inicio, hora_fin = parse_tramo(selected_tramo)
                if not hora_inicio or not hora_fin:
                    messages.error(request, "El tramo horario no es válido.")
                    return redirect(f"{request.path}?user_email={user_email}")

                reserva = Reserva(
                    aula=aula,
                    usuario=user,
                    fecha=selected_date,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    motivo="Reserva desde búsqueda",
                    estado="Pendiente",
                )

                if Reserva.objects.filter(
                    aula=aula,
                    usuario=user,
                    fecha=selected_date,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                ).exists():
                    messages.warning(request, "Ya tienes una solicitud para esa aula, fecha y tramo horario.")
                else:
                    reserva.save()
                    estado_final = reserva.estado

                    if estado_final == "Confirmada":
                        messages.success(request, "Reserva confirmada automáticamente.")
                    else:
                        messages.warning(request, "Reserva denegada, el aula o el usuario ya tienen una reserva a esta hora.")

                    return redirect(f"/mis-reservas/?user_email={user_email}")

    aulas = Aula.objects.all()
    reservas_dia = Reserva.objects.select_related("aula", "usuario").filter(fecha=selected_date).order_by("hora_inicio")

    return render(
        request,
        "buscar_aulas.html",
        {
            "aulas": aulas,
            "reservas_dia": reservas_dia,
            "selected_date": selected_date,
            "selected_tramo": selected_tramo,
            "user_email": get_user_email_from_request(request),
        },
    )


def mis_reservas(request):
    user_email = get_user_email_from_request(request)
    reservas = Reserva.objects.select_related("aula", "usuario", "usuario__perfil").order_by("-fecha", "hora_inicio")
    if user_email:
        reservas = reservas.filter(usuario__email__iexact=user_email)

    total_reservas = reservas.count()
    confirmadas = reservas.filter(estado="Confirmada").count()
    pendientes = reservas.filter(estado="Pendiente").count()

    return render(
        request,
        "mis_reservas.html",
        {
            "reservas": reservas,
            "user_email": user_email,
            "total_reservas": total_reservas,
            "total_confirmadas": confirmadas,
            "total_pendientes": pendientes,
        },
    )


def registrar_incidencia(request):
    if request.method == "POST":
        user_email = get_user_email_from_request(request)
        user = User.objects.filter(email__iexact=user_email).first() if user_email else None
        aula_id = request.POST.get("aula_id")
        tipo = request.POST.get("tipo", "").strip()
        prioridad = request.POST.get("prioridad", "Media").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        aula = Aula.objects.filter(pk=aula_id).first()

        if not user:
            messages.error(request, "No se ha podido identificar el usuario.")
        elif not aula:
            messages.error(request, "Selecciona un aula válida.")
        elif not tipo or not descripcion:
            messages.error(request, "Completa el tipo y la descripción.")
        else:
            Incidencia.objects.create(
                aula=aula,
                usuario=user,
                tipo=tipo,
                prioridad=prioridad if prioridad in {"Baja", "Media", "Alta"} else "Media",
                descripcion=descripcion,
                estado="Pendiente",
            )
            messages.success(request, "Incidencia guardada correctamente.")
            return redirect(f"/historial-incidencias/?user_email={user_email}")

    aulas = Aula.objects.all()
    return render(
        request,
        "registrar_incidencia.html",
        {
            "aulas": aulas,
            "user_email": get_user_email_from_request(request),
        },
    )


def historial_incidencias(request):
    user_email = get_user_email_from_request(request)
    incidencias = Incidencia.objects.select_related("aula", "usuario", "usuario__perfil").order_by("-fecha", "tipo")
    if user_email:
        incidencias = incidencias.filter(usuario__email__iexact=user_email)

    total_incidencias = incidencias.count()
    abiertas = incidencias.filter(estado="Pendiente").count()
    en_curso = incidencias.filter(estado="En curso").count()
    resueltas = incidencias.filter(estado="Resuelta").count()

    return render(
        request,
        "historial_incidencias.html",
        {
            "incidencias": incidencias,
            "user_email": user_email,
            "total_incidencias": total_incidencias,
            "incidencias_abiertas": abiertas,
            "incidencias_en_curso": en_curso,
            "incidencias_resueltas": resueltas,
        },
    )


def gestion_aulas(request):
    is_admin, user_email = require_admin_role(request)
    if not is_admin:
        return redirect(admin_redirect("dashboard_profesor" if user_email else "index", user_email))

    if request.method == "POST":
        aula_id = request.POST.get("aula_id")
        nombre = request.POST.get("nombre", "").strip()
        tipo = request.POST.get("tipo", "Aula normal").strip()
        capacidad = request.POST.get("capacidad", "0").strip()
        estado = request.POST.get("estado", "Disponible").strip()

        if not nombre:
            messages.error(request, "Indica el nombre del aula.")
        else:
            try:
                capacidad_num = int(capacidad)
            except ValueError:
                capacidad_num = 0

            if capacidad_num < 1:
                messages.error(request, "La capacidad debe ser mayor que 0.")
            else:
                with transaction.atomic():
                    aula = Aula.objects.filter(pk=aula_id).first() if aula_id else Aula()
                    aula.nombre = nombre
                    aula.tipo = tipo
                    aula.capacidad = capacidad_num
                    aula.planta = aula.planta or "1ª"
                    aula.estado = estado
                    aula.equipamiento = aula.equipamiento or ""
                    aula.save()
                messages.success(request, "Aula guardada correctamente.")
                return redirect(admin_redirect("gestion_aulas", user_email))

    aulas = Aula.objects.all()
    total_aulas = aulas.count()
    disponibles = aulas.filter(estado="Disponible").count()
    mantenimiento = aulas.filter(estado="Mantenimiento").count()

    return render(
        request,
        "gestion_aulas.html",
        {
            "aulas": aulas,
            "total_aulas": total_aulas,
            "aulas_disponibles": disponibles,
            "aulas_mantenimiento": mantenimiento,
            "user_email": user_email,
        },
    )


def gestion_reservas(request):
    is_admin, user_email = require_admin_role(request)
    if not is_admin:
        return redirect(admin_redirect("dashboard_profesor" if user_email else "index", user_email))

    if request.method == "POST":
        reserva_id = request.POST.get("reserva_id")
        action = (request.POST.get("action") or "").strip().lower()
        reserva = Reserva.objects.filter(pk=reserva_id).first()

        if not reserva:
            messages.error(request, "No se encontró la reserva.")
            return redirect(admin_redirect("gestion_reservas", user_email))

        if action == "validar":
            reserva.estado = "Confirmada"
            reserva.save(update_fields=["estado"])
            messages.success(request, "Reserva validada correctamente.")
        elif action == "denegar":
            reserva.estado = "Denegada"
            reserva.save(update_fields=["estado"])
            messages.warning(request, "Reserva denegada.")
        elif action == "cancelar":
            reserva.estado = "Cancelada"
            reserva.save(update_fields=["estado"])
            messages.warning(request, "Reserva cancelada.")
        elif action == "forzar":
            reserva.estado = "Confirmada"
            reserva.save(update_fields=["estado"])
            messages.success(request, "Reserva confirmada por administrador (forzada).")
        else:
            messages.error(request, "Acción no válida.")

        return redirect(admin_redirect("gestion_reservas", user_email))

    reservas = Reserva.objects.select_related("aula", "usuario").order_by("-fecha", "hora_inicio")
    today = timezone.localdate()
    reservas_hoy = reservas.filter(fecha=today).count()
    pendientes = reservas.filter(estado="Pendiente").count()
    confirmadas = reservas.filter(estado="Confirmada").count()

    return render(
        request,
        "gestion_reservas.html",
        {
            "reservas": reservas,
            "reservas_hoy": reservas_hoy,
            "total_pendientes": pendientes,
            "total_confirmadas": confirmadas,
            "user_email": user_email,
        },
    )


def gestion_incidencias(request):
    is_admin, user_email = require_admin_role(request)
    if not is_admin:
        return redirect(admin_redirect("dashboard_profesor" if user_email else "index", user_email))

    if request.method == "POST":
        incidencia_id = request.POST.get("incidencia_id")
        action = request.POST.get("action")
        incidencia = Incidencia.objects.filter(pk=incidencia_id).first()

        if not incidencia:
            messages.error(request, "No se ha encontrado la incidencia.")
        elif action == "pendiente":
            incidencia.estado = "Pendiente"
            incidencia.save(update_fields=["estado"])
            messages.success(request, "Incidencia marcada como pendiente.")
        elif action == "curso":
            incidencia.estado = "En curso"
            incidencia.save(update_fields=["estado"])
            messages.success(request, "Incidencia marcada como en curso.")
        elif action == "resolver":
            incidencia.estado = "Resuelta"
            incidencia.save(update_fields=["estado"])
            messages.success(request, "Incidencia resuelta.")
        else:
            messages.error(request, "Acción no válida.")

        return redirect(admin_redirect("gestion_incidencias", user_email))

    incidencias = Incidencia.objects.select_related("aula", "usuario", "usuario__perfil").order_by("-fecha", "tipo")
    total_incidencias = incidencias.count()
    abiertas = incidencias.filter(estado="Pendiente").count()
    en_curso = incidencias.filter(estado="En curso").count()
    resueltas = incidencias.filter(estado="Resuelta").count()

    return render(
        request,
        "gestion_incidencias.html",
        {
            "incidencias": incidencias,
            "total_incidencias": total_incidencias,
            "incidencias_abiertas": abiertas,
            "incidencias_en_curso": en_curso,
            "incidencias_resueltas": resueltas,
            "user_email": user_email,
        },
    )


def gestion_usuarios(request):
    is_admin, user_email = require_admin_role(request)
    if not is_admin:
        return redirect(admin_redirect("dashboard_profesor" if user_email else "index", user_email))

    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        rol = request.POST.get("rol", "profesor").strip()
        estado = request.POST.get("estado", "Activo").strip()

        if not nombre or not email:
            messages.error(request, "Rellena nombre y email.")
        elif password and len(password) < 4:
            messages.error(request, "La contraseña debe tener al menos 4 caracteres.")
        else:
            user_qs = User.objects.filter(email__iexact=email)
            if usuario_id:
                user_qs = user_qs.exclude(pk=usuario_id)

            if user_qs.exists():
                messages.error(request, "Ya existe un usuario con ese email.")
            else:
                first_name, last_name = parse_full_name(nombre)
                with transaction.atomic():
                    user = User.objects.filter(pk=usuario_id).first() if usuario_id else User()
                    user.username = email
                    user.email = email
                    user.first_name = first_name
                    user.last_name = last_name
                    if password:
                        user.set_password(password)
                    elif not user.pk:
                        user.set_password("123456")
                    user.save()

                    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
                    perfil.rol = rol if rol in {"profesor", "admin"} else "profesor"
                    perfil.estado = estado if estado in {"Activo", "Bloqueado"} else "Activo"
                    perfil.save()

                if not usuario_id and not password:
                    messages.success(request, "Usuario guardado correctamente. Clave temporal: 123456.")
                else:
                    messages.success(request, "Usuario guardado correctamente.")
                return redirect(admin_redirect("gestion_usuarios", user_email))

    usuarios = User.objects.select_related("perfil").filter(perfil__isnull=False).order_by("first_name", "last_name", "username")
    total_usuarios = usuarios.count()
    profesorado = usuarios.filter(perfil__rol="profesor").count()
    administradores = usuarios.filter(perfil__rol="admin").count()

    return render(
        request,
        "gestion_usuarios.html",
        {
            "usuarios": usuarios,
            "total_usuarios": total_usuarios,
            "total_profesorado": profesorado,
            "total_administradores": administradores,
            "full_name": full_name,
            "user_email": user_email,
        },
    )
