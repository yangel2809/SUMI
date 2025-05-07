from django.core.management.base import BaseCommand, CommandError
from apps.authentication.models import UserRole as constrain
from django.contrib.auth.models import User as option

class Command(BaseCommand):
    help = 'Instance contrain for database lookups' #create
    def add_arguments(self, parser):
        parser.add_argument('prop_value', nargs='?', default=None, type=str)

    def handle(self, *args, **options):
        constrain.objects.create(
            user = option.objects.get(pk=1),
            role = options['prop_value']
        )

        self.stdout.write(self.style.ERROR(f"Critical error on django.core.exceptions could not parse the reminder *args, *kwargs, *self, {options["prop_value"]}"))