from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase

from gestion.models import Aula, PerfilUsuario, Reserva


class ReservaRulesTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            username="a@test.es",
            email="a@test.es",
            password="123456",
        )
        self.user_b = User.objects.create_user(
            username="b@test.es",
            email="b@test.es",
            password="123456",
        )
        PerfilUsuario.objects.create(user=self.user_a, rol="profesor", estado="Activo")
        PerfilUsuario.objects.create(user=self.user_b, rol="profesor", estado="Activo")

        self.aula_1 = Aula.objects.create(
            nombre="Aula Test 1",
            tipo="Aula normal",
            capacidad=30,
            planta="1",
            estado="Disponible",
            equipamiento="",
        )
        self.aula_2 = Aula.objects.create(
            nombre="Aula Test 2",
            tipo="Aula normal",
            capacidad=30,
            planta="1",
            estado="Disponible",
            equipamiento="",
        )

    def test_reserva_pendiente_sin_solape_se_confirma(self):
        reserva = Reserva.objects.create(
            aula=self.aula_1,
            usuario=self.user_a,
            fecha=date(2026, 4, 12),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            motivo="Clase",
            estado=Reserva.Estado.PENDIENTE,
        )

        self.assertEqual(reserva.estado, Reserva.Estado.CONFIRMADA)

    def test_reserva_solape_misma_aula_se_deniega(self):
        Reserva.objects.create(
            aula=self.aula_1,
            usuario=self.user_a,
            fecha=date(2026, 4, 12),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            motivo="Primera",
            estado=Reserva.Estado.CONFIRMADA,
        )

        reserva_conflicto = Reserva.objects.create(
            aula=self.aula_1,
            usuario=self.user_b,
            fecha=date(2026, 4, 12),
            hora_inicio=time(10, 30),
            hora_fin=time(11, 30),
            motivo="Conflicto aula",
            estado=Reserva.Estado.PENDIENTE,
        )

        self.assertEqual(reserva_conflicto.estado, Reserva.Estado.DENEGADA)

    def test_reserva_solape_mismo_usuario_se_deniega(self):
        Reserva.objects.create(
            aula=self.aula_1,
            usuario=self.user_a,
            fecha=date(2026, 4, 12),
            hora_inicio=time(12, 0),
            hora_fin=time(13, 0),
            motivo="Primera",
            estado=Reserva.Estado.CONFIRMADA,
        )

        reserva_conflicto = Reserva.objects.create(
            aula=self.aula_2,
            usuario=self.user_a,
            fecha=date(2026, 4, 12),
            hora_inicio=time(12, 15),
            hora_fin=time(13, 15),
            motivo="Conflicto usuario",
            estado=Reserva.Estado.PENDIENTE,
        )

        self.assertEqual(reserva_conflicto.estado, Reserva.Estado.DENEGADA)
