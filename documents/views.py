from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from .models import Document

@ensure_csrf_cookie
@login_required
@permission_required('documents.delete_document', raise_exception=True)
@require_http_methods(["POST"])
def deleteDocument(request, pk):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return HttpResponseBadRequest('Only AJAX requests are allowed')
    obj = get_object_or_404(Document, pk=pk)
    obj.delete()
    return JsonResponse({'success': True})
