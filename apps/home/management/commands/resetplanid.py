from django.core.management.base import BaseCommand, CommandError
from apps.home.models import Plan, Structure, Test
from apps.home.views import get_id 
from django.db import transaction 

class Command(BaseCommand):
    help = 'Get a plan and set his id to a low available one'
    
    def add_arguments(self, parser):
        parser.add_argument('prop_value', nargs='?', default=None, type=str)
        
    @transaction.atomic
    def handle(self, *args, **options):
        try:
            data = Plan.objects.get(id=options['prop_value'])
            structures = Structure.objects.filter(plan__id=options['prop_value'])
            tests = Test.objects.filter(plan__id=options['prop_value'])
        except Plan.DoesNotExist:
            raise CommandError('Error, Plan does not exist')
        old_id = data.id#type:ignore
        data.id = get_id(Plan)#type:ignore
        data.save()

        for st in structures:
            mat = st.material
            st.id = None #type:ignore
            st.plan = data #type:ignore
            st.save()
            for m in mat.all():
                st.material.add(m)        

        new_tests = []
        for ts in tests:
            ts.id = None #type:ignore
            ts.plan = data #type:ignore
            new_tests.append(ts)

        Test.objects.bulk_create(new_tests)

        Plan.objects.get(id=options['prop_value']).delete()
        
        self.stdout.write(self.style.SUCCESS(f"Success Plan ID={old_id} changed to ID={data.id}"))#type: ignore