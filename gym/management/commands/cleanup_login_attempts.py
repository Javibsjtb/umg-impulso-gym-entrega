from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from gym.models import LoginThrottle

class Command(BaseCommand):
    help = 'Elimina contadores de intentos que expiraron hace más de un día.'
    def handle(self, *args, **options):
        count, _ = LoginThrottle.objects.filter(window_start__lt=timezone.now()-timedelta(days=1)).delete()
        self.stdout.write(f'{count} contadores eliminados.')
