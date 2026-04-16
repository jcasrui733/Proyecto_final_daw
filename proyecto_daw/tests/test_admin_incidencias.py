from django.contrib.auth.models import User
from django.test import TestCase

from gestion.models import Aula, Incidencia, PerfilUsuario


class IncidenciasAndAdminFlowsTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin@test.es",
            email="admin@test.es",
            password="123456",
        )
        PerfilUsuario.objects.create(user=self.admin_user, rol="admin", estado="Activo")

        self.profesor = User.objects.create_user(
            username="profe2@test.es",
            email="profe2@test.es",
            password="123456",
        )
        PerfilUsuario.objects.create(user=self.profesor, rol="profesor", estado="Activo")

        self.aula = Aula.objects.create(
            nombre="Aula Incidencias",
            tipo="Aula normal",
            capacidad=20,
            planta="1",
            estado="Disponible",
            equipamiento="",
        )

    def test_registrar_incidencia_crea_pendiente(self):
        response = self.client.post(
            "/registrar-incidencia/?user_email=profe2@test.es",
            {
                "user_email": "profe2@test.es",
                "aula_id": self.aula.id,
                "tipo": "Proyector roto",
                "prioridad": "Alta",
                "descripcion": "No enciende",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        incidencia = Incidencia.objects.filter(usuario=self.profesor, aula=self.aula, tipo="Proyector roto").latest("id")
        self.assertEqual(incidencia.estado, "Pendiente")

    def test_admin_crea_usuario_profesor(self):
        scenarios = [
            {
                "nombre": "Docente Nuevo",
                "email": "docente.nuevo@test.es",
                "rol": "profesor",
            },
            {
                "nombre": "Admin Nuevo",
                "email": "admin.nuevo@test.es",
                "rol": "admin",
            },
        ]

        for scenario in scenarios:
            with self.subTest(rol=scenario["rol"]):
                response = self.client.post(
                    "/gestion-usuarios/?user_email=admin@test.es",
                    {
                        "user_email": "admin@test.es",
                        "nombre": scenario["nombre"],
                        "email": scenario["email"],
                        "password": "1234",
                        "rol": scenario["rol"],
                        "estado": "Activo",
                    },
                    follow=True,
                )

                self.assertEqual(response.status_code, 200)
                created = User.objects.get(email=scenario["email"])
                self.assertEqual(created.perfil.rol, scenario["rol"])

