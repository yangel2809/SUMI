#Copyright (c) 2022 - present, Daniel Escalona

from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib.staticfiles import finders

def render_to_pdf(template, context={}):
    template = get_template(template)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf8')), result)
    if not pdf.err:
        
        return HttpResponse(result.getvalue(), content_type='aplication/pdf')
        
    return HttpResponse()

#--------------------------------------------------------------------->
def csrf_failure(request, reason=""):
    return redirect('/logout')
def page_400(request, exception):
    return render(request, 'errors/400.html', status=400)
    
def page_403(request, exception):
    return render(request, 'errors/403.html', status=403)

def page_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def page_500(request):
    return render(request, 'errors/500.html')