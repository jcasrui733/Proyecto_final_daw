from django.contrib.auth.models import User
from django.test import TestCase

from gestion.models import PerfilUsuario


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profesor@test.es",
            email="profesor@test.es",
            password="123456",
            first_name="Profe",
            last_name="Uno",
        )
        PerfilUsuario.objects.create(user=self.user, rol="profesor", estado="Activo")

    def test_api_login_ok(self):
        response = self.client.post(
            "/api/login/",
            {"email": "profesor@test.es", "password": "123456"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["user"]["rol"], "profesor")

    def test_api_login_blocked_user(self):
        perfil = self.user.perfil
        perfil.estado = "Bloqueado"
        perfil.save(update_fields=["estado"])

        response = self.client.post(
            "/api/login/",
            {"email": "profesor@test.es", "password": "123456"},
        )

        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertFalse(payload["ok"])
