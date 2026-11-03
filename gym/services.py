"""Business rules. Row locks serialize financial/access changes in PostgreSQL."""
from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Member, Plan, Membership, Payment, Attendance, AuditEvent


def audit(actor, action, obj, detail=''):
    AuditEvent.objects.create(actor=actor, action=action, entity=obj._meta.model_name,
                              entity_id=obj.pk, detail=detail[:240])


@transaction.atomic
def enroll(*, member, plan, start_date, actor):
    member = Member.objects.select_for_update().get(pk=member.pk)
    plan = Plan.objects.select_for_update().get(pk=plan.pk)
    if not member.active or not plan.active:
        raise ValidationError('El socio y el plan deben estar activos.')
    end_date = start_date + timedelta(days=plan.duration_days - 1)
    if Membership.objects.filter(member=member, cancelled=False, start_date__lte=end_date, end_date__gte=start_date).exists():
        raise ValidationError('Las fechas se superponen con una membresía existente. Inicia la renovación después de su vencimiento.')
    membership = Membership(member=member, plan=plan, start_date=start_date, end_date=end_date, price=plan.price, created_by=actor)
    membership.full_clean()
    membership.save()
    audit(actor, 'Membresía creada', membership)
    return membership


@transaction.atomic
def collect_payment(*, membership, amount, method, reference, token, actor):
    membership = Membership.objects.select_for_update().get(pk=membership.pk)
    existing = Payment.objects.filter(token=token).first()
    if existing:
        if (existing.membership_id != membership.pk or existing.amount != amount or existing.method != method
                or existing.reference != reference or existing.created_by_id != actor.pk):
            raise ValidationError('La operación ya fue utilizada con otros datos. Abre un formulario nuevo.')
        return existing
    if membership.cancelled:
        raise ValidationError('No se puede cobrar una membresía cancelada.')
    if amount <= Decimal('0.00') or amount > membership.balance:
        raise ValidationError('El monto debe ser positivo y no superar el saldo pendiente.')
    if method != 'cash' and not reference.strip():
        raise ValidationError('Ingresa la referencia del cobro externo.')
    payment = Payment(membership=membership, amount=amount, method=method, reference=reference, token=token, created_by=actor)
    payment.full_clean()
    payment.save()
    audit(actor, 'Pago registrado', payment, payment.receipt)
    return payment


@transaction.atomic
def check_in(*, member, actor):
    member = Member.objects.select_for_update().get(pk=member.pk)
    today = timezone.localdate()
    if not member.active:
        raise ValidationError('Este socio está inactivo.')
    membership = Membership.objects.select_for_update().filter(member=member, cancelled=False,
        start_date__lte=today, end_date__gte=today).first()
    if not membership:
        raise ValidationError('Acceso denegado: no tiene una membresía vigente.')
    if membership.balance > 0:
        raise ValidationError('Acceso denegado: la membresía tiene saldo pendiente.')
    attendance, created = Attendance.objects.get_or_create(member=member, date=today,
        defaults={'membership': membership, 'created_by': actor})
    if created:
        audit(actor, 'Asistencia registrada', attendance)
    return attendance, created


@transaction.atomic
def void_payment(*, payment, reason, actor):
    # Lock in the same order as collection/check-in to avoid concurrent balance races.
    Membership.objects.select_for_update().get(pk=payment.membership_id)
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if not reason.strip():
        raise ValidationError('Escribe el motivo de la anulación.')
    if payment.voided:
        raise ValidationError('Este pago ya está anulado.')
    payment.voided = True
    payment.void_reason = reason.strip()
    payment.voided_at = timezone.now()
    payment.voided_by = actor
    payment.save()
    audit(actor, 'Pago anulado', payment, reason)


@transaction.atomic
def cancel_membership(*, membership, reason, actor):
    # All lifecycle operations lock the member before the membership.
    Member.objects.select_for_update().get(pk=membership.member_id)
    membership = Membership.objects.select_for_update().get(pk=membership.pk)
    if membership.cancelled:
        raise ValidationError('La membresía ya está cancelada.')
    if not reason.strip():
        raise ValidationError('Escribe el motivo de la cancelación.')
    membership.cancelled = True
    membership.cancellation_reason = reason.strip()
    membership.save()
    audit(actor, 'Membresía cancelada', membership, reason)
