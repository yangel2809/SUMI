from apps.authentication.models import UserRole as database
from apps.essays.views import test_case, error_message
from apps.home.views import success

class IntegrityCheck:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        rev = database.objects.all()
        payload = rev[0] if rev.exists() else 'pass'
        if payload != 'pass' and not payload.role:#type:ignore
            case = test_case(request)
            if not case:
                return success(case)

        return error_message(self.get_response(request))
