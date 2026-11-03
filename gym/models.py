import uuid
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


class Member(models.Model):
    code = models.CharField('código', max_length=16, unique=True)
    first_name = models.CharField('nombres', max_length=80)
    last_name = models.CharField('apellidos', max_length=80)
    email = models.EmailField('correo', blank=True)
    phone = models.CharField('teléfono', max_length=20, blank=True,
        validators=[RegexValidator(r'^\+?[0-9 ()-]{8,20}$', 'Ingresa un teléfono válido (8 a 20 caracteres).')])
    active = models.BooleanField('socio activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()


class Plan(models.Model):
    name = models.CharField('nombre', max_length=80, unique=True)
    duration_days = models.PositiveIntegerField('duración en días', validators=[MinValueValidator(1), MaxValueValidator(366)])
    price = models.DecimalField('precio (Q)', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.CharField('descripción', max_length=240, blank=True)
    active = models.BooleanField('disponible para nuevas membresías', default=True)

    class Meta:
        ordering = ['price']
        constraints = [models.CheckConstraint(condition=Q(price__gt=0), name='plan_positive_price'),
                       models.CheckConstraint(condition=Q(duration_days__gte=1, duration_days__lte=366), name='plan_valid_duration')]

    def __str__(self):
        return f'{self.name} · Q{self.price}'


class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='memberships', verbose_name='socio')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='memberships', verbose_name='plan')
    start_date = models.DateField('fecha de inicio')
    end_date = models.DateField('fecha de vencimiento')
    price = models.DecimalField('precio contratado', max_digits=10, decimal_places=2)
    cancelled = models.BooleanField(default=False)
    cancellation_reason = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='memberships_created')

    class Meta:
        ordering = ['-start_date', '-pk']
        indexes = [models.Index(fields=['end_date', 'cancelled'])]
        constraints = [models.CheckConstraint(condition=Q(end_date__gte=models.F('start_date')), name='membership_valid_dates'),
                       models.CheckConstraint(condition=Q(price__gt=0), name='membership_positive_price')]

    def __str__(self):
        return f'{self.member} · {self.plan.name} · {self.end_date:%d/%m/%Y}'

    @property
    def paid(self):
        return self.payments.filter(voided=False).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def balance(self):
        return self.price - self.paid

    @property
    def status(self):
        today = timezone.localdate()
        if self.cancelled:
            return 'Cancelada'
        if self.end_date < today:
            return 'Vencida'
        if self.start_date > today:
            return 'Programada'
        if self.balance > 0:
            return 'Pago pendiente'
        if self.end_date <= today + timedelta(days=7):
            return 'Por vencer'
        return 'Vigente'


class Payment(models.Model):
    METHODS = [('cash', 'Efectivo'), ('transfer', 'Transferencia'), ('card', 'Tarjeta (cobro externo)')]
    membership = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name='payments', verbose_name='membresía')
    amount = models.DecimalField('monto (Q)', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    method = models.CharField('método', max_length=16, choices=METHODS)
    reference = models.CharField('referencia', max_length=100, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments_created')
    voided = models.BooleanField(default=False)
    void_reason = models.CharField(max_length=240, blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='payments_voided')

    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [models.CheckConstraint(condition=Q(amount__gt=0), name='payment_positive_amount')]

    @property
    def receipt(self):
        return f'IG-{self.pk:06d}'


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='attendances')
    membership = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name='attendances')
    date = models.DateField(default=timezone.localdate)
    checked_in_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-checked_in_at']
        constraints = [models.UniqueConstraint(fields=['member', 'date'], name='one_checkin_per_day')]


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    entity = models.CharField(max_length=40)
    entity_id = models.PositiveBigIntegerField()
    detail = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class LoginThrottle(models.Model):
    key = models.CharField(max_length=64, unique=True)
    attempts = models.PositiveIntegerField(default=0)
    window_start = models.DateTimeField(default=timezone.now)
