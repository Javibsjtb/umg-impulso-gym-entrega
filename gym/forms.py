import uuid
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Member, Plan, Payment
from .permissions import MANAGER, RECEPTION


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['code', 'first_name', 'last_name', 'email', 'phone', 'active']

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        if not code.replace('-', '').isalnum():
            raise forms.ValidationError('Usa letras, números o guiones.')
        if Member.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este código ya está registrado.')
        return code


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'duration_days', 'price', 'description', 'active']


class EnrollmentForm(forms.Form):
    member = forms.ModelChoiceField(label='Socio', queryset=Member.objects.filter(active=True))
    plan = forms.ModelChoiceField(label='Plan', queryset=Plan.objects.filter(active=True))
    start_date = forms.DateField(label='Fecha de inicio', initial=timezone.localdate, widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))


class PaymentForm(forms.Form):
    amount = forms.DecimalField(label='Monto (Q)', max_digits=10, decimal_places=2, min_value=0.01)
    method = forms.ChoiceField(label='Método de pago', choices=Payment.METHODS)
    reference = forms.CharField(label='Referencia del cobro externo', max_length=100, required=False,
        help_text='Obligatoria para transferencia o tarjeta. No ingreses números de tarjeta.')
    token = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)


class CheckInForm(forms.Form):
    code = forms.CharField(label='Código del socio', max_length=16, widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Ej. IG-001', 'autocomplete': 'off'}))


class ReasonForm(forms.Form):
    reason = forms.CharField(label='Motivo', min_length=5, max_length=240, widget=forms.Textarea(attrs={'rows': 3}))


class StaffUserForm(UserCreationForm):
    role = forms.ChoiceField(label='Rol', choices=[(RECEPTION, RECEPTION), (MANAGER, MANAGER)])
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']


class StaffEditForm(forms.ModelForm):
    role = forms.ChoiceField(label='Rol', choices=[(RECEPTION, RECEPTION), (MANAGER, MANAGER)])
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'role']


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}))
