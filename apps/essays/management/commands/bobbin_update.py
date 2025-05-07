from django.core.management.base import BaseCommand
from apps.essays.models import Bobbin, TestFileEssayResult

class Command(BaseCommand):
    help = 'Migrates Bobbin test_file field'

    def handle(self, *args, **options):
        for bobbin in Bobbin.objects.all():
            # Get the associated TestFileEssayResult
            testfileessayresult = TestFileEssayResult.objects.filter(bobbin=bobbin).first()

            if testfileessayresult:
                # Set the test_file field on the Bobbin instance
                bobbin.test_file = testfileessayresult.essay.test_file#type:ignore
                bobbin.save()

        self.stdout.write(self.style.SUCCESS('Successfully migrated Bobbin test_file field'))
