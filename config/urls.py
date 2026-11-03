from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path
from gym import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', v.health, name='health'),
    path('login/', v.StaffLoginView.as_view(), name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
    path('cuenta/password/', auth.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url='/cuenta/password/listo/'), name='password_change'),
    path('cuenta/password/listo/', auth.PasswordChangeDoneView.as_view(template_name='registration/password_done.html'), name='password_change_done'),
    path('', v.home, name='home'),
    path('panel/', v.dashboard, name='dashboard'),
    path('socios/', v.member_list, name='members'),
    path('socios/nuevo/', v.member_edit, name='member_create'),
    path('socios/<int:pk>/', v.member_detail, name='member_detail'),
    path('socios/<int:pk>/editar/', v.member_edit, name='member_edit'),
    path('socios/<int:pk>/eliminar/', v.member_delete, name='member_delete'),
    path('planes/', v.plans, name='plans'),
    path('planes/nuevo/', v.plan_edit, name='plan_create'),
    path('planes/<int:pk>/editar/', v.plan_edit, name='plan_edit'),
    path('planes/<int:pk>/eliminar/', v.plan_delete, name='plan_delete'),
    path('membresias/', v.memberships, name='memberships'),
    path('membresias/nueva/', v.membership_create, name='membership_create'),
    path('membresias/<int:pk>/cancelar/', v.membership_cancel, name='membership_cancel'),
    path('membresias/<int:pk>/pagar/', v.payment_create, name='payment_create'),
    path('pagos/', v.payments, name='payments'),
    path('pagos/<int:pk>/', v.receipt, name='receipt'),
    path('pagos/<int:pk>/anular/', v.payment_void, name='payment_void'),
    path('asistencia/', v.attendance, name='attendance'),
    path('api/socios/', v.member_lookup, name='member_lookup'),
    path('reportes/', v.reports, name='reports'),
    path('equipo/', v.users, name='users'),
    path('equipo/nuevo/', v.user_edit, name='user_create'),
    path('equipo/<int:pk>/editar/', v.user_edit, name='user_edit'),
    path('auditoria/', v.audit_log, name='audit'),
]
