from django.conf import settings
from .permissions import is_manager

def brand(request):
    return {'gym_name': settings.GYM_NAME, 'gym_phone': settings.GYM_PHONE, 'demo_mode': settings.DEMO_MODE,
            'manager': is_manager(request.user)}
