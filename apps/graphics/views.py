import http
import datetime, decimal, re
from django.db import transaction
from django.http import JsonResponse,HttpResponse, Http404, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Q
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, permission_required

from apps.essays.models import ArtRequest
from apps.graphics.models import *
from apps.production.models import Order, PrinterBoot, LaminatorBoot, CutterBoot
from apps.sales.models import SaleOrder

@login_required(login_url='/login/')
@permission_required('production.view_printerboot', raise_exception=True)
def OrderPrePrintStatusDetails(request, pk, ck):
    
    order_obj = get_object_or_404(Order, pk=pk)
    pre_print_status = get_object_or_404(PrinterBoot, pk=ck)

    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)

    content ='graphics/details/pre_print_status.html'
    context = {
        'order_obj':order_obj,
        'pre_print_status':pre_print_status,
        'tab':'printer_boot',
        'segment':'order',
        'detail':'production',
        'back': True,
        'content':content,
        'tab_s':pre_print_status.id, #type:ignore
        #render tabs--------------------
        'printer_boot':printer_boot,
        'laminator_boot':laminator_boot,
        'cutter_boot': cutter_boot,

    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)

def update_pre_print_status(request):
    if request.method == 'POST':
        soid = request.POST.get('soid')
        sost = request.POST.get('sost')
        nature = request.POST.get('nature')

        so = get_object_or_404(SaleOrder, pk=soid)
        error = render(request, 'errors/400.html', status=400)

        if nature == 'reject':
            try:
                pre_print = PrePrint.objects.get(sale_order_id=soid)
            except PrePrint.DoesNotExist:
                return JsonResponse({'error': 'Invalid request method'})
            
            if sost == 'pp_pdf_approval':
                pre_print.pdf = False
                reject = PdfRejects.objects.create(status=pre_print, date = timezone.now())

            elif sost == 'pp_pc_approval':
                pre_print.pc = False
                reject = PCRejects.objects.create(status=pre_print, date = timezone.now())

            pre_print.save()
            reject.save()
            context = {'sale_order':so}
            response = render_to_string('sales/formsets/sale-status.html', context, request)

            return JsonResponse({'response': response, 'success': True})
        
        elif nature == 'check':
            try:
                pre_print = PrePrint.objects.get(sale_order_id=soid)
            except PrePrint.DoesNotExist:
                pre_print = PrePrint.objects.create(sale_order_id=soid)

            # Update PrePrint fields based on sost
            if so.origin in ['upd', 'new']:
                if sost == 'pp_pdf_check':
                    pre_print.pdf = True
                    pre_print.pdf_date = timezone.now()
                elif sost == 'pp_pdf_approval':
                    pre_print.pdf_approval = True
                    pre_print.pdf_approval_date = timezone.now()
                elif sost == 'pp_pc_check':
                    pre_print.pc = True
                    pre_print.pc_date = timezone.now()
                elif sost == 'pp_pc_approval':
                    pre_print.pc_approval = True
                    pre_print.pc_approval_date = timezone.now()
                elif sost == 'pp_plate':
                    pre_print.plates = True
                    pre_print.plates_date = timezone.now()
                    so.pre_print_ready = True
                    so.save()
                else:
                    return error
            elif so.origin == 'pro':
                if sost == 'pp_plate':
                    pre_print.plates = True
                    pre_print.plates_date = timezone.now()
                    so.pre_print_ready = True
                    so.save()
                else:
                    return error
            else:
                return error

            pre_print.save()
            context = {'sale_order':so}
            response = render_to_string('sales/formsets/sale-status.html', context, request)
            
            return JsonResponse({'response': response, 'success': True})
        
    return JsonResponse({'error': 'Invalid request method'})

@login_required(login_url='/login/')
@permission_required('production.view_printerboot', raise_exception=True)
def test_email(request):
    test_request = get_object_or_404(ArtRequest, pk=6)
    context= {
        'request': request,
        'obj':test_request,
        }
    html_message = render_to_string('graphics/email.html', context)
    subject = "Notificación SUMI"
    from_email = "danieldaxter159@gmail.com"
    recipient_list = ["emailtestcase@proton.me", "danieldaxter159@gmail.com"]

    
    email = EmailMessage(subject, html_message, from_email, recipient_list)
    email.content_subtype = 'html'  # Set the content subtype to HTML
    email.send()

    #return render(request, 'graphics/email.html', context)

    return HttpResponse('yei')
