from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username='judge').exists():
            User.objects.create_superuser('judge', '', 'AnchorPay2026!')
            self.stdout.write(self.style.SUCCESS('Judge account created'))
        else:
            self.stdout.write('Judge account already exists')