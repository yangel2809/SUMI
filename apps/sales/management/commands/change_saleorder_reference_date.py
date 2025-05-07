from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from apps.sales.models import SaleOrder

class Command(BaseCommand):
    help = 'Change the reference_date of a SaleOrder object'

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, help='ID of the SaleOrder object')
        parser.add_argument('date', type=str, help='New reference_date in YYYY-MM-DD HH:MM:SS format')

    def handle(self, *args, **options):
        id = options['id']
        date_str = options['date']
        date = parse_datetime(date_str)

        if not date:
            raise CommandError('Invalid date format. Use YYYY-MM-DD HH:MM:SS')

        # Make the datetime timezone aware
        date = timezone.make_aware(date)

        try:
            sale_order = SaleOrder.objects.get(pk=id)
        except SaleOrder.DoesNotExist:
            raise CommandError('SaleOrder with id "%s" does not exist' % id)

        sale_order.reference_date = date
        sale_order.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated SaleOrder id "%s"' % id))
