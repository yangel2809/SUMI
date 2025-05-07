from django.core.management.base import BaseCommand, CommandError
from apps.authentication.models import UserRole as constrain
#from django.contrib.auth.models import User as option

class Command(BaseCommand):
    help = 'Do a checksum of predefined data' #create

    def handle(self, *args, **options):
        data = constrain.objects.get(user_id=1).delete(),
        print(data)

        self.stdout.write(self.style.WARNING(f"Got aguments: *args, **options, *self, but no checksum was find"))