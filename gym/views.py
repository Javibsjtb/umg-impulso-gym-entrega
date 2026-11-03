import csv
import hashlib
import hmac
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction, connection
from django.db.models import Count, F, Q, Sum
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import MemberForm, PlanForm, EnrollmentForm, PaymentForm, CheckInForm, ReasonForm, StaffUserForm, StaffEditForm, LoginForm
from .models import Member, Plan, Membership, Payment, Attendance, AuditEvent, LoginThrottle
from .permissions import staff_required, is_manager, MANAGER, RECEPTION
from .services import enroll, collect_payment, check_in, void_payment, cancel_membership, audit


def pages(request, objects):
    return Paginator(objects, 15).get_page(request.GET.get('page'))


class StaffLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '')[:150].strip().lower()
        key = hmac.new(settings.SECRET_KEY.encode(), username.encode(), hashlib.sha256).hexdigest()
        with transaction.atomic():
            LoginThrottle.objects.get_or_create(key=key)
            throttle = LoginThrottle.objects.select_for_update().get(key=key)
            if timezone.now() - throttle.window_start > timedelta(minutes=15):
                throttle.attempts = 0
                throttle.window_start = timezone.now()
            if throttle.attempts >= 5:
                form = self.get_form()
                form.add_error(None, 'Demasiados intentos. Intenta nuevamente en 15 minutos.')
                return self.render_to_response(self.get_context_data(form=form), status=429)
            form = self.get_form()
            if form.is_valid():
                throttle.delete()
                return self.form_valid(form)
            throttle.attempts += 1
            throttle.save()
        return self.form_invalid(form)


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return JsonResponse({'status': 'ok'})
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)


@require_GET
def home(request):
    return render(request, 'gym/home.html', {'public_plans': Plan.objects.filter(active=True)})


@staff_required
def dashboard(request):
    today = timezone.localdate()
    current = Membership.objects.filter(cancelled=False, member__active=True, start_date__lte=today, end_date__gte=today)
    paid_current = current.annotate(paid_total=Sum('payments__amount', filter=Q(payments__voided=False))).filter(paid_total__gte=F('price'))
    income = Payment.objects.filter(voided=False, created_at__date__gte=today.replace(day=1)).aggregate(total=Sum('amount'))['total'] or 0
    days = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        days.append({'label': day.strftime('%d/%m'), 'count': Attendance.objects.filter(date=day).count(), 'today': offset == 0})
    max_count = max([d['count'] for d in days] + [1])
    for index, day in enumerate(days):
        day.update({'x': 30 + index * 75, 'y': 155 - int(day['count'] / max_count * 115), 'height': max(2, int(day['count'] / max_count * 115))})
    return render(request, 'gym/dashboard.html', {
        'today': today, 'active_members': paid_current.values('member_id').distinct().count(),
        'total_members': Member.objects.filter(active=True).count(), 'income': income,
        'today_attendance': Attendance.objects.filter(date=today).count(),
        'expiring_count': current.filter(end_date__lte=today+timedelta(days=7)).count(),
        'expiring': current.filter(end_date__lte=today+timedelta(days=7)).select_related('member', 'plan').order_by('end_date', 'member__first_name')[:5],
        'recent': Attendance.objects.select_related('member')[:5], 'days': days,
        'latest_payments': Payment.objects.filter(voided=False).select_related('membership__member')[:4]})


@staff_required
def member_list(request):
    q = request.GET.get('q', '').strip()[:100]
    status = request.GET.get('status', '')
    members = Member.objects.all()
    if q:
        members = members.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(code__icontains=q) | Q(email__icontains=q))
    if status in ('active', 'inactive'):
        members = members.filter(active=status == 'active')
    return render(request, 'gym/members.html', {'page': pages(request, members), 'q': q, 'status': status,
                                               'total': Member.objects.count(), 'active_count': Member.objects.filter(active=True).count()})


@staff_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'gym/member_detail.html', {'member': member,
        'memberships': member.memberships.select_related('plan'),
        'payments': Payment.objects.filter(membership__member=member).select_related('created_by')[:15],
        'attendances': member.attendances.all()[:10]})


@staff_required
def member_edit(request, pk=None):
    with transaction.atomic():
        member = get_object_or_404(Member.objects.select_for_update(), pk=pk) if pk else None
        form = MemberForm(request.POST or None, instance=member)
        if request.method == 'POST' and form.is_valid():
            member = form.save()
            audit(request.user, 'Socio actualizado' if pk else 'Socio creado', member)
            messages.success(request, 'Ficha del socio guardada.')
            return redirect('member_detail', pk=member.pk)
    return render(request, 'gym/form.html', {'form': form, 'title': 'Editar socio' if pk else 'Nuevo socio',
        'subtitle': 'Una ficha clara para acompañar cada entrenamiento.', 'back': reverse('members')})


@staff_required(manager=True)
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            try:
                audit(request.user, 'Socio eliminado', member)
                member.delete()
            except ProtectedError:
                transaction.set_rollback(True)
                messages.error(request, 'Tiene historial asociado. Desactívalo desde su ficha para conservar la trazabilidad.')
                return redirect('member_detail', pk=pk)
        messages.success(request, 'Socio eliminado.')
        return redirect('members')
    return render(request, 'gym/confirm.html', {'title': 'Eliminar socio', 'object': member,
        'explanation': 'Solo es posible eliminar fichas sin membresías ni asistencias. Si tiene historial, utiliza la opción de desactivar.', 'back': reverse('member_detail', args=[pk])})


@staff_required
def plans(request):
    return render(request, 'gym/plans.html', {'plans': Plan.objects.annotate(subscriptions=Count('memberships'))})


@staff_required(manager=True)
def plan_edit(request, pk=None):
    with transaction.atomic():
        plan = get_object_or_404(Plan.objects.select_for_update(), pk=pk) if pk else None
        form = PlanForm(request.POST or None, instance=plan)
        if request.method == 'POST' and form.is_valid():
            plan = form.save()
            audit(request.user, 'Plan actualizado' if pk else 'Plan creado', plan)
            messages.success(request, 'Plan guardado. Las membresías anteriores conservan su precio y duración.')
            return redirect('plans')
    return render(request, 'gym/form.html', {'form': form, 'title': 'Editar plan' if pk else 'Crear plan',
        'subtitle': 'Define el precio y la duración para las nuevas membresías.', 'back': reverse('plans')})


@staff_required(manager=True)
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            try:
                audit(request.user, 'Plan eliminado', plan)
                plan.delete()
            except ProtectedError:
                transaction.set_rollback(True)
                messages.error(request, 'El plan tiene membresías. Puedes desactivarlo para impedir nuevas inscripciones.')
                return redirect('plans')
        messages.success(request, 'Plan eliminado.')
        return redirect('plans')
    return render(request, 'gym/confirm.html', {'title': 'Eliminar plan', 'object': plan,
        'explanation': 'Los planes con membresías se conservan. Puedes desactivarlos desde Editar.', 'back': reverse('plans')})


@staff_required
def memberships(request):
    today = timezone.localdate()
    q = request.GET.get('q', '').strip()[:100]
    status = request.GET.get('status', '')
    objects = Membership.objects.select_related('member', 'plan')
    if q:
        objects = objects.filter(Q(member__first_name__icontains=q) | Q(member__last_name__icontains=q) | Q(member__code__icontains=q))
    if status == 'expiring':
        objects = objects.filter(cancelled=False, start_date__lte=today, end_date__range=(today, today+timedelta(days=7)))
    elif status == 'expired':
        objects = objects.filter(cancelled=False, end_date__lt=today)
    elif status == 'current':
        objects = objects.filter(cancelled=False, start_date__lte=today, end_date__gte=today)
    elif status == 'cancelled':
        objects = objects.filter(cancelled=True)
    return render(request, 'gym/memberships.html', {'page': pages(request, objects), 'q': q, 'status': status})


@staff_required
def membership_create(request):
    initial = {}
    if request.GET.get('plan', '').isdigit():
        plan = Plan.objects.filter(pk=request.GET['plan'], active=True).first()
        if plan:
            initial['plan'] = plan
    if request.GET.get('member', '').isdigit():
        member = Member.objects.filter(pk=request.GET['member'], active=True).first()
        if member:
            initial['member'] = member
            last = member.memberships.filter(cancelled=False).order_by('-end_date').first()
            if last:
                initial['start_date'] = max(timezone.localdate(), last.end_date + timedelta(days=1))
    form = EnrollmentForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        try:
            membership = enroll(**form.cleaned_data, actor=request.user)
            messages.success(request, 'Membresía creada. Registra el pago para habilitar el acceso.')
            return redirect('payment_create', pk=membership.pk)
        except ValidationError as exc:
            form.add_error(None, exc)
    return render(request, 'gym/form.html', {'form': form, 'title': 'Nueva membresía',
        'subtitle': 'La fecha de vencimiento se calcula automáticamente; el último día está incluido.', 'back': reverse('memberships')})


@staff_required(manager=True)
def membership_cancel(request, pk):
    membership = get_object_or_404(Membership.objects.select_related('member'), pk=pk)
    form = ReasonForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            cancel_membership(membership=membership, reason=form.cleaned_data['reason'], actor=request.user)
            messages.success(request, 'Membresía cancelada. Los pagos se conservan; la cancelación no implica un reembolso.')
            return redirect('member_detail', pk=membership.member_id)
        except ValidationError as exc:
            form.add_error(None, exc)
    return render(request, 'gym/form.html', {'form': form, 'title': 'Cancelar membresía',
        'subtitle': f'{membership}. Los pagos no se reembolsan automáticamente.', 'back': reverse('memberships')})


@staff_required
def payment_create(request, pk):
    membership = get_object_or_404(Membership.objects.select_related('member', 'plan'), pk=pk)
    form = PaymentForm(request.POST or None, initial={'amount': membership.balance})
    if request.method == 'POST' and form.is_valid():
        try:
            payment = collect_payment(membership=membership, actor=request.user, **form.cleaned_data)
            messages.success(request, 'Pago registrado correctamente.')
            return redirect('receipt', pk=payment.pk)
        except ValidationError as exc:
            form.add_error(None, exc)
    return render(request, 'gym/form.html', {'form': form, 'title': 'Registrar pago',
        'subtitle': f'{membership.member} · {membership.plan.name} · Saldo: Q{membership.balance:.2f}',
        'back': reverse('member_detail', args=[membership.member_id])})


@staff_required
def payments(request):
    q = request.GET.get('q', '').strip()[:100]
    objects = Payment.objects.select_related('membership__member', 'created_by')
    if q:
        objects = objects.filter(Q(membership__member__first_name__icontains=q) | Q(membership__member__last_name__icontains=q) |
                                  Q(membership__member__code__icontains=q) | Q(reference__icontains=q))
    return render(request, 'gym/payments.html', {'page': pages(request, objects), 'q': q})


@staff_required
def receipt(request, pk):
    return render(request, 'gym/receipt.html', {'payment': get_object_or_404(Payment.objects.select_related('membership__member', 'membership__plan', 'created_by', 'voided_by'), pk=pk)})


@staff_required(manager=True)
def payment_void(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    form = ReasonForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            void_payment(payment=payment, reason=form.cleaned_data['reason'], actor=request.user)
            messages.success(request, 'Pago anulado. El saldo de la membresía fue recalculado.')
            return redirect('receipt', pk=pk)
        except ValidationError as exc:
            form.add_error(None, exc)
    return render(request, 'gym/form.html', {'form': form, 'title': f'Anular {payment.receipt}',
        'subtitle': 'Utiliza esta operación para corregir un registro erróneo. No ejecuta una devolución bancaria.', 'back': reverse('receipt', args=[pk])})


@staff_required
def attendance(request):
    form = CheckInForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        member = Member.objects.filter(code=form.cleaned_data['code'].strip().upper()).first()
        if not member:
            form.add_error('code', 'No se encontró un socio con ese código.')
        else:
            try:
                entry, created = check_in(member=member, actor=request.user)
                if created:
                    messages.success(request, f'¡Adelante, {member.first_name}! Asistencia registrada.')
                else:
                    messages.info(request, f'{member} ya tiene una asistencia registrada hoy.')
                return redirect('attendance')
            except ValidationError as exc:
                form.add_error(None, exc)
    today = timezone.localdate()
    return render(request, 'gym/attendance.html', {'form': form, 'today': today,
        'page': pages(request, Attendance.objects.filter(date=today).select_related('member', 'created_by'))})


@staff_required
@require_GET
def member_lookup(request):
    q = request.GET.get('q', '').strip()[:80]
    if len(q) < 2:
        return JsonResponse({'results': []})
    objects = Member.objects.filter(Q(code__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)).order_by('first_name')[:8]
    return JsonResponse({'results': [{'code': m.code, 'name': str(m), 'active': m.active} for m in objects]})


@staff_required(manager=True)
def reports(request):
    from django import forms
    class RangeForm(forms.Form):
        start = forms.DateField(label='Desde', widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
        end = forms.DateField(label='Hasta', widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
        def clean(self):
            data = super().clean()
            if data.get('start') and data.get('end') and data['start'] > data['end']:
                raise forms.ValidationError('La fecha inicial debe ser anterior o igual a la final.')
            return data
    today = timezone.localdate()
    form = RangeForm(request.GET or {'start': today.replace(day=1), 'end': today})
    objects = Payment.objects.none()
    if form.is_valid():
        objects = Payment.objects.filter(created_at__date__range=(form.cleaned_data['start'], form.cleaned_data['end'])).select_related('membership__member', 'created_by')
    valid = objects.filter(voided=False)
    total = valid.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    if request.GET.get('format') == 'csv' and form.is_valid():
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="reporte-pagos.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Comprobante', 'Fecha', 'Código socio', 'Socio', 'Monto Q', 'Método', 'Estado'])
        def safe(value):
            value = str(value)
            return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else value
        for p in objects:
            writer.writerow([p.receipt, timezone.localtime(p.created_at).isoformat(), safe(p.membership.member.code), safe(p.membership.member), p.amount, p.get_method_display(), 'Anulado' if p.voided else 'Registrado'])
        return response
    return render(request, 'gym/reports.html', {'form': form, 'total': total, 'count': valid.count(),
        'voided_count': objects.filter(voided=True).count(), 'by_method': valid.values('method').annotate(total=Sum('amount')).order_by('method'),
        'page': pages(request, objects), 'valid_range': form.is_valid()})


@staff_required(manager=True)
def users(request):
    return render(request, 'gym/users.html', {'users': User.objects.prefetch_related('groups').order_by('username')})


@staff_required(manager=True)
def user_edit(request, pk=None):
    user = get_object_or_404(User, pk=pk) if pk else None
    if user and user.is_superuser:
        messages.error(request, 'La cuenta de mantenimiento se administra desde Django Admin.')
        return redirect('users')
    form = StaffEditForm(request.POST or None, instance=user, initial={'role': MANAGER if user and is_manager(user) else RECEPTION}) if pk else StaffUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if user and user.pk == request.user.pk and (not form.cleaned_data['is_active'] or form.cleaned_data['role'] != MANAGER):
            form.add_error(None, 'No puedes quitarte tu propio acceso administrativo.')
        else:
            with transaction.atomic():
                user = form.save()
                user.groups.set([Group.objects.get_or_create(name=form.cleaned_data['role'])[0]])
                audit(request.user, 'Usuario actualizado' if pk else 'Usuario creado', user)
            messages.success(request, 'Usuario guardado.')
            return redirect('users')
    return render(request, 'gym/form.html', {'form': form, 'title': 'Editar usuario' if pk else 'Nuevo usuario',
        'subtitle': 'Cada persona debe utilizar su propia cuenta.', 'back': reverse('users')})


@staff_required(manager=True)
def audit_log(request):
    return render(request, 'gym/audit.html', {'page': pages(request, AuditEvent.objects.select_related('actor'))})
