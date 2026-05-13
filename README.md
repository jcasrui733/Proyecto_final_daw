# ACR_Aulas

## Descripción

Este proyecto es una aplicación web desarrollada con Django que permite la gestión integral de aulas, reservas e incidencias en un centro educativo. Incluye un sistema de autenticación, paneles diferenciados para profesores y administradores, y funcionalidades para registrar y gestionar incidencias, reservas y usuarios.

## Características principales

- **Autenticación de usuarios**: Registro y login mediante endpoints API (`/api/register/` y `/api/login/`).
- **Panel de profesor**: Visualización de próximas reservas, incidencias recientes y aulas disponibles.
- **Panel de administrador**: Acceso a la gestión de aulas, reservas, incidencias y usuarios.
- **Gestión de aulas**: Alta, edición y consulta de aulas, con información de capacidad, tipo y estado.
- **Gestión de reservas**: Solicitud, validación, denegación y cancelación de reservas de aulas.
- **Gestión de incidencias**: Registro y seguimiento de incidencias en las aulas, con distintos estados (pendiente, en curso, resuelta).
- **Gestión de usuarios**: Alta, edición y asignación de roles (profesor o administrador), así como activación o bloqueo de cuentas.
- **Consumo de APIs internas**: El frontend consume los endpoints internos para login y registro, devolviendo y mostrando información en formato JSON.
- **Interfaz responsiva**: Navegación sencilla y adaptada a distintos dispositivos.

## Estructura del proyecto

- **proyecto_daw/**: Configuración principal de Django, vistas y rutas.
- **gestion/**: Modelos y lógica de negocio.
- **frontend/static/**: Archivos estáticos (JS, CSS, imágenes).
- **templates/**: Plantillas HTML para las distintas vistas.
- **www/**: Archivos de despliegue (Docker, Nginx, requirements).

## Funcionamiento

1. **Inicio de sesión y registro**:  
   Los usuarios pueden registrarse y autenticarse mediante los endpoints `/api/register/` y `/api/login/`. El frontend realiza peticiones HTTP a estas APIs y muestra los resultados en la interfaz.

2. **Navegación**:  
   Tras iniciar sesión, los profesores acceden a su panel personalizado, donde pueden ver y gestionar sus reservas e incidencias. Los administradores disponen de un panel con acceso a la gestión global del sistema.

3. **Gestión de aulas, reservas e incidencias**:  
   - Los profesores pueden buscar aulas disponibles y solicitar reservas.
   - Pueden registrar incidencias en las aulas y consultar su historial.
   - Los administradores pueden validar, denegar o cancelar reservas, así como gestionar el estado de las incidencias y los datos de los usuarios.

4. **Despliegue**:  
   El proyecto puede ejecutarse en local con Django o desplegarse en producción usando Docker y Nginx.

