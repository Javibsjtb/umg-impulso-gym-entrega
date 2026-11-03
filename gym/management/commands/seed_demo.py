import os
import secrets
import uuid
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from gym.models import Member, Plan, Membership, Payment, Attendance
from gym.permissions import MANAGER, RECEPTION
from gym.services import enroll, collect_payment


class Command(BaseCommand):
    help = 'Carga datos completamente ficticios, únicamente con DEBUG y DEMO_MODE activos.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG or not settings.DEMO_MODE:
            raise CommandError('La demo requiere DEBUG=True y DEMO_MODE=True. No usar en producción.')
        if Member.objects.exists() or User.objects.filter(username='admin.demo').exists():
            self.stdout.write('La base ya contiene datos. No se modificó ningún registro ni contraseña.')
            return
        password = os.getenv('DEMO_PASSWORD') or secrets.token_urlsafe(15)
        admin = User.objects.create_user('admin.demo', password=password, first_name='Administración', last_name='Demo')
        reception = User.objects.create_user('recepcion.demo', password=password, first_name='Recepción', last_name='Demo')
        admin.groups.add(Group.objects.get_or_create(name=MANAGER)[0])
        reception.groups.add(Group.objects.get_or_create(name=RECEPTION)[0])
        plans = [Plan.objects.create(name=n, duration_days=d, price=p, description=desc) for n, d, p, desc in [
            ('Esencial', 30, Decimal('180.00'), 'Tu rutina comienza aquí. Acceso al área de entrenamiento.'),
            ('Constancia', 60, Decimal('330.00'), 'Dos meses para construir un hábito y seguir avanzando.'),
            ('Progreso', 90, Decimal('450.00'), 'Tres meses de compromiso con tu siguiente meta.')]]
        names = [('Ana','López'),('Diego','Méndez'),('Valeria','Castro'),('Mateo','Ramírez'),('Sofía','Morales'),
                 ('Andrés','Vega'),('Camila','Ríos'),('Gabriel','Pérez'),('Lucía','Herrera'),('Daniel','Soto'),
                 ('Isabella','Cruz'),('Sebastián','Díaz'),('Mariana','Flores'),('Nicolás','Ruiz'),('Paula','Reyes'),
                 ('Alejandro','Luna'),('Victoria','Paz'),('Samuel','Ortega'),('Renata','León'),('Emilio','Fuentes'),
                 ('Elena','Campos'),('Tomás','Aguilar'),('Julia','Rosales'),('Lucas','Vargas')]
        today = timezone.localdate()
        for i, (first, last) in enumerate(names):
            member = Member.objects.create(code=f'IG-{i+1:03}', first_name=first, last_name=last, email=f'socio{i+1}@example.com')
            start = today - timedelta(days=24-i%5) if i < 16 else today-timedelta(days=45)
            if i in (20,21):
                start = today
            if i >= 22:
                start = today+timedelta(days=3)
            plan = plans[0] if i < 20 else plans[1]
            membership = enroll(member=member, plan=plan, start_date=start, actor=admin)
            if i != 21:
                payment = collect_payment(membership=membership, amount=plan.price if i != 20 else Decimal('100.00'),
                    method='cash' if i%3 else 'transfer', reference='' if i%3 else f'DEMO-{i+1:03}', token=uuid.uuid4(), actor=reception)
                Payment.objects.filter(pk=payment.pk).update(created_at=timezone.now()-timedelta(days=i%12))
            if i < 16:
                for offset in range(7):
                    if (i+offset)%3 == 0:
                        entry = Attendance.objects.create(member=member, membership=membership,
                            date=today-timedelta(days=offset), created_by=reception)
                        Attendance.objects.filter(pk=entry.pk).update(checked_in_at=timezone.now()-timedelta(days=offset, minutes=i*11))
            if i == 19:
                member.active = False
                member.save()
        self.stdout.write(self.style.SUCCESS('Demo creada: 24 socios ficticios, 3 planes, membresías, pagos y asistencias.'))
        self.stdout.write(f'Usuarios: admin.demo / recepcion.demo\nContraseña para ambos: {password}')
        self.stdout.write('Guarda la contraseña localmente. Nunca cargues estos datos en un entorno productivo.')
