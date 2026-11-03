import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest import skipUnless
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, connections, close_old_connections, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .forms import MemberForm, PlanForm
from .models import Member, Plan, Membership, Payment, Attendance, AuditEvent, LoginThrottle
from .permissions import MANAGER, RECEPTION
from .services import enroll, collect_payment, check_in, void_payment, cancel_membership


class Fixtures:
    def build(self):
        self.admin = User.objects.create_user('manager', password='Manager-pass-908!')
        self.admin.groups.add(Group.objects.get_or_create(name=MANAGER)[0])
        self.reception = User.objects.create_user('desk', password='Reception-pass-908!')
        self.reception.groups.add(Group.objects.get_or_create(name=RECEPTION)[0])
        self.member = Member.objects.create(code='IG-001', first_name='Ana', last_name='Demo')
        self.plan = Plan.objects.create(name='Mensual', duration_days=30, price=Decimal('180.00'))
        self.today = timezone.localdate()
        self.membership = enroll(member=self.member, plan=self.plan, start_date=self.today, actor=self.admin)

    def pay(self, amount=Decimal('180.00'), **kwargs):
        data = dict(membership=self.membership, amount=amount, method='cash', reference='', token=uuid.uuid4(), actor=self.reception)
        data.update(kwargs)
        return collect_payment(**data)


@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class BusinessTests(Fixtures, TestCase):
    def setUp(self):
        self.build()

    def test_duration_includes_last_day(self):
        self.assertEqual(self.membership.end_date, self.today + timedelta(days=29))

    def test_overlap_rejected(self):
        with self.assertRaises(ValidationError):
            enroll(member=self.member, plan=self.plan, start_date=self.today+timedelta(days=29), actor=self.admin)
        self.assertEqual(Membership.objects.count(), 1)

    def test_renewal_starts_after_end(self):
        renewed = enroll(member=self.member, plan=self.plan, start_date=self.today+timedelta(days=30), actor=self.admin)
        self.assertEqual(renewed.status, 'Programada')

    def test_price_and_dates_snapshot(self):
        self.plan.price = Decimal('250.00'); self.plan.duration_days = 10; self.plan.save()
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.price, Decimal('180.00'))
        self.assertEqual(self.membership.end_date, self.today+timedelta(days=29))

    def test_inactive_member_cannot_enroll(self):
        self.member.active = False; self.member.save()
        with self.assertRaises(ValidationError):
            enroll(member=self.member, plan=self.plan, start_date=self.today+timedelta(days=30), actor=self.admin)

    def test_inactive_plan_cannot_enroll(self):
        self.plan.active = False; self.plan.save()
        with self.assertRaises(ValidationError):
            enroll(member=self.member, plan=self.plan, start_date=self.today+timedelta(days=30), actor=self.admin)

    def test_partial_payment_and_balance(self):
        self.pay(Decimal('50.00'))
        self.assertEqual(self.membership.balance, Decimal('130.00'))
        self.assertEqual(self.membership.status, 'Pago pendiente')

    def test_payment_over_balance_rejected(self):
        with self.assertRaises(ValidationError): self.pay(Decimal('180.01'))
        self.assertEqual(Payment.objects.count(), 0)

    def test_zero_negative_payment_rejected(self):
        for amount in (Decimal('0'), Decimal('-1')):
            with self.assertRaises(ValidationError): self.pay(amount)

    def test_external_payment_requires_reference(self):
        with self.assertRaises(ValidationError): self.pay(method='transfer')
        self.assertEqual(Payment.objects.count(), 0)

    def test_payment_idempotency(self):
        token = uuid.uuid4()
        first = self.pay(token=token)
        second = self.pay(token=token)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Payment.objects.count(), 1)

    def test_reused_token_different_data_rejected(self):
        token = uuid.uuid4(); self.pay(Decimal('50'), token=token)
        with self.assertRaises(ValidationError): self.pay(Decimal('40'), token=token)

    def test_paid_member_can_check_in(self):
        self.pay(); attendance, created = check_in(member=self.member, actor=self.reception)
        self.assertTrue(created)
        self.assertEqual(attendance.membership, self.membership)

    def test_checkin_idempotency(self):
        self.pay(); first, _ = check_in(member=self.member, actor=self.reception)
        second, created = check_in(member=self.member, actor=self.reception)
        self.assertFalse(created); self.assertEqual(first.pk, second.pk)
        self.assertEqual(Attendance.objects.count(), 1)

    def test_unpaid_checkin_rejected(self):
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)

    def test_partial_payment_checkin_rejected(self):
        self.pay(Decimal('50'))
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)

    def test_expired_checkin_rejected(self):
        self.pay(); self.membership.start_date = self.today-timedelta(days=30)
        self.membership.end_date = self.today-timedelta(days=1); self.membership.save()
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)

    def test_last_day_checkin_allowed(self):
        self.pay(); self.membership.end_date = self.today; self.membership.save()
        _, created = check_in(member=self.member, actor=self.reception)
        self.assertTrue(created)

    def test_future_membership_no_access(self):
        self.pay(); self.membership.start_date = self.today+timedelta(days=1); self.membership.save()
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)

    def test_inactive_member_no_access(self):
        self.pay(); self.member.active = False; self.member.save()
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)

    def test_void_keeps_record_and_restores_balance(self):
        payment = self.pay()
        void_payment(payment=payment, reason='Registro duplicado externo', actor=self.admin)
        payment.refresh_from_db()
        self.assertTrue(payment.voided); self.assertEqual(payment.voided_by, self.admin)
        self.assertEqual(self.membership.balance, Decimal('180'))
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)
        self.assertEqual(Payment.objects.count(), 1)

    def test_cannot_void_twice(self):
        payment = self.pay(); void_payment(payment=payment, reason='Corrección', actor=self.admin)
        with self.assertRaises(ValidationError): void_payment(payment=payment, reason='Otra corrección', actor=self.admin)

    def test_cancel_keeps_payments_and_prevents_access(self):
        payment = self.pay()
        cancel_membership(membership=self.membership, reason='Solicitado por socio', actor=self.admin)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, 'Cancelada'); self.assertEqual(self.membership.paid, Decimal('180'))
        with self.assertRaises(ValidationError): check_in(member=self.member, actor=self.reception)
        with self.assertRaises(ValidationError): self.pay(Decimal('1'))

    def test_audit_tracks_real_actor(self):
        payment = self.pay()
        event = AuditEvent.objects.get(action='Pago registrado')
        self.assertEqual(event.actor, self.reception); self.assertEqual(event.entity_id, payment.pk)

    def test_db_rejects_invalid_amount(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Payment.objects.create(membership=self.membership, amount=-1, method='cash', created_by=self.admin)

    def test_member_form_validates_email_phone_duplicate(self):
        form = MemberForm(data={'code':'ig-001','first_name':'X','last_name':'Y','email':'bad','phone':'abc','active':True})
        self.assertFalse(form.is_valid()); self.assertIn('code',form.errors); self.assertIn('email',form.errors); self.assertIn('phone',form.errors)

    def test_plan_validates_duration_and_price(self):
        form = PlanForm(data={'name':'Bad','duration_days':0,'price':-1,'active':True})
        self.assertFalse(form.is_valid()); self.assertIn('duration_days',form.errors); self.assertIn('price',form.errors)


@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class WebTests(Fixtures, TestCase):
    def setUp(self):
        self.build(); self.client.force_login(self.admin)

    def test_all_pages_render(self):
        payment = self.pay()
        routes = ['dashboard','members','member_create','plans','plan_create','memberships','membership_create',
                  'payments','attendance','reports','users','user_create','audit','password_change']
        for name in routes:
            with self.subTest(name=name): self.assertEqual(self.client.get(reverse(name)).status_code,200)
        for name, pk in [('member_detail',self.member.pk),('member_edit',self.member.pk),('member_delete',self.member.pk),
                         ('plan_edit',self.plan.pk),('plan_delete',self.plan.pk),('payment_create',self.membership.pk),
                         ('membership_cancel',self.membership.pk),('receipt',payment.pk),('payment_void',payment.pk),('user_edit',self.reception.pk)]:
            with self.subTest(name=name): self.assertEqual(self.client.get(reverse(name,args=[pk])).status_code,200)

    def test_public_home_exposes_only_active_plans(self):
        self.client.logout()
        Plan.objects.create(name='Hidden draft', duration_days=30, price=100, active=False)
        response = self.client.get('/')
        self.assertContains(response, self.plan.name)
        self.assertNotContains(response, 'Hidden draft')
        self.assertContains(response, '/login/')

    def test_selected_public_plan_prefills_enrollment(self):
        response = self.client.get('/membresias/nueva/', {'plan': self.plan.pk})
        self.assertEqual(response.context['form'].initial['plan'], self.plan)

    def test_anonymous_redirect(self):
        self.client.logout()
        for name in ['dashboard','members','plans','payments','attendance','member_lookup','reports','users','audit']:
            with self.subTest(name=name): self.assertEqual(self.client.get(reverse(name)).status_code,302)

    def test_user_without_role_forbidden(self):
        user=User.objects.create_user('outsider',password='Outside-pass-123!'); self.client.force_login(user)
        self.assertEqual(self.client.get('/panel/').status_code,403)
        self.assertEqual(self.client.get('/api/socios/?q=Ana').status_code,403)

    def test_reception_cannot_administer_get_or_post(self):
        payment=self.pay(); self.client.force_login(self.reception)
        paths=['/reportes/','/equipo/','/equipo/nuevo/','/auditoria/','/planes/nuevo/',
               f'/planes/{self.plan.pk}/editar/',f'/planes/{self.plan.pk}/eliminar/',
               f'/socios/{self.member.pk}/eliminar/',f'/pagos/{payment.pk}/anular/',f'/membresias/{self.membership.pk}/cancelar/']
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code,403)
                self.assertEqual(self.client.post(path,{'reason':'No autorizado'}).status_code,403)

    def test_reception_can_complete_workflow(self):
        self.client.force_login(self.reception)
        response=self.client.post('/socios/nuevo/',{'code':'IG-002','first_name':'Pedro','last_name':'Demo','active':True})
        self.assertEqual(response.status_code,302)
        member=Member.objects.get(code='IG-002')
        response=self.client.post('/membresias/nueva/',{'member':member.pk,'plan':self.plan.pk,'start_date':self.today.isoformat()})
        self.assertEqual(response.status_code,302)
        membership=Membership.objects.get(member=member)
        response=self.client.post(f'/membresias/{membership.pk}/pagar/',{'amount':'180.00','method':'cash','reference':'','token':str(uuid.uuid4())})
        self.assertEqual(response.status_code,302)
        payment = Payment.objects.get(membership=membership)
        self.assertContains(self.client.get(response.url), payment.receipt)
        response=self.client.post('/asistencia/',{'code':'ig-002'})
        self.assertEqual(response.status_code,302); self.assertTrue(Attendance.objects.filter(member=member).exists())

    def test_invalid_form_does_not_mutate(self):
        count=Member.objects.count()
        self.assertEqual(self.client.post('/socios/nuevo/',{'code':'','first_name':'','last_name':''}).status_code,200)
        self.assertEqual(Member.objects.count(),count)

    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True); client.force_login(self.admin)
        self.assertEqual(client.post('/socios/nuevo/',{'code':'IG-002'}).status_code,403)

    def test_get_does_not_delete_and_post_protects_history(self):
        self.client.get(f'/socios/{self.member.pk}/eliminar/')
        self.assertTrue(Member.objects.filter(pk=self.member.pk).exists())
        response=self.client.post(f'/socios/{self.member.pk}/eliminar/')
        self.assertEqual(response.status_code,302); self.assertTrue(Member.objects.filter(pk=self.member.pk).exists())
        self.assertFalse(AuditEvent.objects.filter(action='Socio eliminado').exists())

    def test_delete_unused_member_and_plan(self):
        member=Member.objects.create(code='EMPTY',first_name='Empty',last_name='Demo')
        plan=Plan.objects.create(name='Empty',duration_days=1,price=1)
        self.client.post(f'/socios/{member.pk}/eliminar/'); self.client.post(f'/planes/{plan.pk}/eliminar/')
        self.assertFalse(Member.objects.filter(pk=member.pk).exists()); self.assertFalse(Plan.objects.filter(pk=plan.pk).exists())

    def test_search_and_pagination(self):
        for i in range(20): Member.objects.create(code=f'Z{i}',first_name=f'Other{i}',last_name='Demo')
        response=self.client.get('/socios/?q=Other&page=2')
        self.assertEqual(len(response.context['page']),5)
        self.assertContains(response,'q=Other'); self.assertNotContains(response,'??')
        self.assertEqual(self.client.get('/socios/?q=Ana').context['page'].paginator.count,1)

    def test_full_name_search_across_workflows(self):
        self.pay()
        for path in ['/socios/', '/membresias/', '/pagos/']:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path, {'q': 'Ana Demo'}).context['page'].paginator.count, 1)
        result = self.client.get('/api/socios/', {'q': 'Ana Demo'}).json()['results']
        self.assertEqual([item['code'] for item in result], ['IG-001'])

    def test_lookup_limits_and_authorization(self):
        response=self.client.get('/api/socios/?q=An')
        self.assertEqual(response.json()['results'][0]['code'],'IG-001')
        self.assertNotIn('email',response.json()['results'][0])
        self.assertEqual(self.client.get('/api/socios/?q=A').json()['results'],[])
        self.assertEqual(self.client.post('/api/socios/').status_code,405)

    def test_expiry_filter(self):
        self.membership.end_date=self.today+timedelta(days=3); self.membership.save()
        self.assertEqual(self.client.get('/membresias/?status=expiring').context['page'].paginator.count,1)

    def test_report_excludes_void_and_csv_escapes_formulas(self):
        self.member.first_name='=SUM(1)'; self.member.save()
        first=self.pay(Decimal('50')); self.pay(Decimal('130'))
        void_payment(payment=first,reason='Corrección',actor=self.admin)
        response=self.client.get('/reportes/')
        self.assertEqual(response.context['total'],Decimal('130'))
        response=self.client.get('/reportes/',{'start':self.today.isoformat(),'end':self.today.isoformat(),'format':'csv'})
        self.assertContains(response,"'=SUM(1)"); self.assertContains(response,'Anulado')

    def test_report_invalid_dates(self):
        response=self.client.get('/reportes/?start=not-a-date&end=bad')
        self.assertEqual(response.status_code,200); self.assertFalse(response.context['valid_range'])
        response=self.client.get('/reportes/',{'start':self.today.isoformat(),'end':(self.today-timedelta(days=1)).isoformat()})
        self.assertFalse(response.context['valid_range'])

    def test_attendance_history_date_filter_and_csv(self):
        self.pay()
        check_in(member=self.member, actor=self.reception)
        yesterday = self.today - timedelta(days=1)
        self.membership.start_date = yesterday
        self.membership.save(update_fields=['start_date'])
        Attendance.objects.create(member=self.member, membership=self.membership, date=yesterday, created_by=self.reception)
        self.assertEqual(self.client.get('/asistencia/').context['page'].paginator.count, 1)
        historical = self.client.get('/asistencia/', {'date': yesterday.isoformat()})
        self.assertEqual(historical.context['page'].paginator.count, 1)
        self.assertEqual(historical.context['page'][0].date, yesterday)
        invalid = self.client.get('/asistencia/', {'date': 'bad-date'})
        self.assertEqual(invalid.status_code, 200)
        self.assertIn('date', invalid.context['date_form'].errors)
        self.member.first_name = '=FORMULA'; self.member.save()
        response = self.client.get('/reportes/', {'start': self.today.isoformat(), 'end': self.today.isoformat(), 'format': 'attendance_csv'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('reporte-asistencia.csv', response['Content-Disposition'])
        self.assertContains(response, "'=FORMULA")
        self.assertContains(response, 'IG-001')
        self.client.force_login(self.reception)
        self.assertEqual(self.client.get('/reportes/', {'start': self.today.isoformat(), 'end': self.today.isoformat(), 'format': 'attendance_csv'}).status_code, 403)

    def test_output_escapes_xss(self):
        self.member.first_name='<script>alert(1)</script>'; self.member.save()
        response=self.client.get('/socios/')
        self.assertNotContains(response,'<script>alert(1)</script>'); self.assertContains(response,'&lt;script&gt;')

    def test_headers_and_post_only_logout(self):
        response=self.client.get('/')
        self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
        self.assertEqual(response.headers['X-Frame-Options'],'DENY')
        self.assertIn('no-store',response.headers['Cache-Control'])
        self.assertEqual(self.client.get('/logout/').status_code,405)
        self.assertEqual(self.client.post('/logout/').status_code,302)

    def test_cannot_remove_own_admin_role(self):
        response=self.client.post(f'/equipo/{self.admin.pk}/editar/',{'first_name':'Admin','last_name':'Demo','email':'','role':RECEPTION,'is_active':True})
        self.assertEqual(response.status_code,200); self.assertTrue(self.admin.groups.filter(name=MANAGER).exists())

    def test_admin_create_reception_user(self):
        response=self.client.post('/equipo/nuevo/',{'username':'newdesk','first_name':'New','last_name':'Desk','email':'','role':RECEPTION,'password1':'Strong-desktop-123!','password2':'Strong-desktop-123!'})
        self.assertEqual(response.status_code,302)
        user=User.objects.get(username='newdesk'); self.assertTrue(user.check_password('Strong-desktop-123!'))
        self.assertFalse(user.is_staff); self.assertTrue(user.groups.filter(name=RECEPTION).exists())

    def test_login_and_throttle(self):
        self.client.logout()
        for _ in range(5): self.client.post('/login/',{'username':'manager','password':'bad'})
        response=self.client.post('/login/',{'username':'manager','password':'Manager-pass-908!'})
        self.assertEqual(response.status_code,429)
        LoginThrottle.objects.update(window_start=timezone.now()-timedelta(minutes=16))
        self.assertEqual(self.client.post('/login/',{'username':'manager','password':'Manager-pass-908!'}).status_code,302)

    def test_login_does_not_redirect_to_external_host(self):
        self.client.logout()
        response=self.client.post('/login/?next=https://evil.example',{'username':'manager','password':'Manager-pass-908!'})
        self.assertEqual(response.url,'/panel/')

    def test_health(self):
        self.client.logout(); self.assertEqual(self.client.get('/health/').json(),{'status':'ok'})

    @override_settings(DEBUG=False,DEMO_MODE=False)
    def test_demo_guard(self):
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError): call_command('seed_demo',stdout=StringIO())


@skipUnless(connection.vendor=='postgresql','PostgreSQL required for row-lock concurrency tests')
class ConcurrencyTests(Fixtures, TransactionTestCase):
    def setUp(self): self.build()

    def worker(self, kind, token=None):
        close_old_connections()
        try:
            if kind=='pay': self.pay(Decimal('100'),token=token or uuid.uuid4())
            elif kind=='check': check_in(member=self.member,actor=self.reception)
            else: enroll(member=self.member,plan=self.plan,start_date=self.today+timedelta(days=30),actor=self.admin)
            return 'ok'
        except ValidationError: return 'rejected'
        finally: connections.close_all()

    def test_simultaneous_payments_cannot_overpay(self):
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(self.worker,['pay','pay']))
        self.assertCountEqual(results,['ok','rejected']); self.assertEqual(self.membership.paid,Decimal('100'))

    def test_simultaneous_checkins_create_one(self):
        self.pay()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(self.worker,['check','check']))
        self.assertEqual(results,['ok','ok']); self.assertEqual(Attendance.objects.count(),1)

    def test_simultaneous_enrollments_cannot_overlap(self):
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(self.worker,['enroll','enroll']))
        self.assertCountEqual(results,['ok','rejected']); self.assertEqual(Membership.objects.count(),2)
