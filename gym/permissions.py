from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

MANAGER = 'Administración'
RECEPTION = 'Recepción'

def is_manager(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name=MANAGER).exists())

def staff_required(view=None, *, manager=False):
    def decorator(fn):
        @login_required
        @wraps(fn)
        def inner(request, *args, **kwargs):
            allowed = is_manager(request.user) or (not manager and request.user.groups.filter(name=RECEPTION).exists())
            if not allowed:
                raise PermissionDenied
            return fn(request, *args, **kwargs)
        return inner
    return decorator(view) if view else decorator
