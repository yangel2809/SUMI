# -*- encoding: utf-8 -*-

# Copyright (c) 2022 - present Daniel Escalona
import datetime, decimal, re
from io import BytesIO
from PIL import Image, ImageOps, JpegImagePlugin
Image.MAX_IMAGE_PIXELS = 999999999 
from copy import deepcopy
from django.db import transaction
from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.files import File
from django.views.generic import ListView
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
#app imports------------------------------------------------------->
from apps.essays.models import Annex, ArtRequest, PrinterBoot as EssaysPrinterBoot, LaminatorBoot as EssaysLaminatorBoot, LaminationEssay as EssaysLaminationEssay, TestFile as EssaysTestFile, TestFileEssay as EssaysTestFileEssay, TestFileEssayResult as EssaysTestFileEssayResult, Bobbin as EssaysBobbin
from apps.sales.models import SaleOrder
from apps.home.models import Structure
from .models import *
from .forms import *

def get_nested_attr(obj, attr):
    for a in attr.split('.'):
        obj = getattr(obj, a)
    return obj

@login_required(login_url="/login/")
def test_or_order(request):
    search_text = request.GET.get('search_text')
    current_op = request.GET.get('current_op')
    current_tr = request.GET.get('current_tr')

    def get_data(model, current, prefix, display_fields, filter_fields):
        if current:
            objs = model.objects.exclude(Q(pk=current)|Q(deleted=True))
        if search_text:
            query = Q()
            for field in filter_fields:
                query |= Q(**{f"{field}__icontains": search_text})
            objs = objs.filter(query)

        if model == Order:
            objs = objs.exclude(sale_order__archived=True)
            return [{'id': f'{prefix}-{obj.id}',  'text': f'{prefix}-{get_nested_attr(obj, display_fields[0])} - {get_nested_attr(obj, display_fields[1])}'} for obj in objs]
        elif model == ArtRequest:
            objs = objs.exclude(reviewer=None)
            return [{'id': f'{prefix}-{obj.id}',  'text': f'Solicitud de Prueba - {get_nested_attr(obj, display_fields[1])}'} if obj.production_order is None else {'id': f'{prefix}-{obj.id}',  'text': f'{prefix}-{get_nested_attr(obj, display_fields[0])} - {get_nested_attr(obj, display_fields[1])}'} for obj in objs]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = get_data(Order, current_op, 'OP', ['number', 'sale_order.plan.product'], ['number', 'sale_order__plan__product'])
        data += get_data(ArtRequest, current_tr, 'PR', ['production_order', 'product'], ['production_order', 'product'])#type: ignore
        return JsonResponse(data, safe=False)
        
    raise Http404


def average(*args, essay=None):
    try:
        args = [float(arg) for arg in args if arg is not None]
        if len(args) == 0:
            return None
        average = sum(args) / len(args)
        if essay and essay.essay and essay.essay.method in ['009', '003', '029', '005']:
            return "{:.2f}".format(average)
        elif essay and essay.essay:
            return str(decimal.Decimal(average).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        else:
            return average
    except TypeError:
        return "Error: Sólo números."
    
@login_required(login_url="/login/")
@permission_required('production.add_order', raise_exception=True)
def OrderAssign(request):
    if request.method == 'POST':
        form = OpAsignForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    return JsonResponse({'status':'error', 'message': 'error'})

class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    permission_required = 'production.view_order'
    model = Order
    template_name = 'production/tables-orders.html'
    context_object_name = 'obj_list'
    paginate_by = 15
    orphans = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Expedientes de Producción'
        context['segment'] = 'order'
        context['search'] = True
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(deleted=True)
        search_text = self.request.GET.get('search_text', None)
        if search_text:
             queryset = queryset.filter(
                Q(sale_order__plan__product__icontains=search_text)|
                Q(sale_order__plan__client__name__icontains=search_text)|
                Q(number__icontains=search_text)|
                Q(date__icontains=search_text)
            )
        return queryset.order_by('number')

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table_html = render_to_string('production/tables/orders.html', context, request=self.request)
            paginator_html = render_to_string('production/paginators/obj.html', context, request=self.request)
            return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        else:
            return super().render_to_response(context, **response_kwargs)

@login_required(login_url="/login/")
@permission_required('production.view_order', raise_exception=True)
def OrderDetails(request, pk):
    order_obj = get_object_or_404(Order, pk=pk)
    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)
    content = 'production/details/order.html'

    context = {
        'order_obj': order_obj,
        'printer_boot': printer_boot,
        'laminator_boot': laminator_boot,
        'cutter_boot': cutter_boot,
        'content': content,
        'segment': 'order',
        'detail':'production',
        'back': True,
        'tab': 'main',
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)

@login_required(login_url="/login/")
@permission_required('production.change_order', raise_exception=True)
def OrderEdit(request, pk):
    obj = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OpAsignForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('order_list')
        else:
            print(form.errors)
    
    return JsonResponse({'status':'error', 'message': 'error'})

@login_required(login_url="/login/")
@permission_required('production.delete_order', raise_exception=True)
def OrderDelete(request, pk):
    order = get_object_or_404(Order, pk=pk)
     
    if order.deleted:
        return render(request, 'errors/403.html', status=403)
        
    order.deleted = True
    order.deleted_by = request.user.username
    order.deleted_time = timezone.now()

    order.save()

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
        
    return redirect('order_list') 


#Printer Boot------------------------------------------------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('production.add_printerboot', raise_exception=True)#type:ignore
def OrderPrinterBootAdd (request, pk):
    
    order_obj = get_object_or_404(Order, pk=pk)
    form = PrinterBootForm(request.POST or None)
    
    context = {'form': form, 'order_obj':order_obj, 'segment':'order', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            printer_boot = form.save(commit=False)
            #validation
            for i in range(1, 11):
                attr = f'sta_{i:02d}'
                value = getattr(printer_boot, attr, None)
                if value is not None:
                    setattr(printer_boot, attr, value.upper())

            printer_boot.production_order = order_obj

            printer_boot.r_average = average(printer_boot.r_left, printer_boot.r_right, printer_boot.r_center)            

            printer_boot.save()

            return redirect(f'/production/{order_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'production/forms/form-printer_boot.html', context)

@login_required(login_url='/login/')
@permission_required('production.add_printerboot', raise_exception=True)#type:ignore
def OrderPrinterBootEdit (request, pk, ck):
    
    order_obj = get_object_or_404(Order, pk=pk)#Get the parent to render
    printer_boot_obj = get_object_or_404(PrinterBoot, pk=ck)

    form = PrinterBootForm(request.POST or None, instance=printer_boot_obj)
    
    context = {'form': form, 'order_obj':order_obj, 'printer_boot_obj':printer_boot_obj, 'segment':'order', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            printer_boot = form.save(commit=False)
            #validation
            for i in range(1, 11):
                attr = f'sta_{i:02d}'
                value = getattr(printer_boot, attr, None)
                if value is not None:
                    setattr(printer_boot, attr, value.upper())

            printer_boot.production_order = order_obj

            printer_boot.r_average = average(printer_boot.r_left, printer_boot.r_right, printer_boot.r_center)            

            printer_boot.save()

            return redirect(f'/production/{order_obj.id}/printer/{printer_boot_obj.id}/') #type:ignore
        else:
            print(form.errors)
    return render(request, 'production/forms/form-printer_boot.html', context)

@login_required(login_url='/login/')
@permission_required('production.delete_printerboot', raise_exception=True)
def OrderPrinterBootDelete(request, pk):

    obj = get_object_or_404(PrinterBoot, id=pk)
    order = obj.production_order.id#type:ignore

    if request.method == 'POST':
        obj.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))

    return redirect('order_details', order)

@login_required(login_url='/login/')
@permission_required('production.view_printerboot', raise_exception=True)
def OrderPrinterBootDetails(request, pk, ck):
    
    order_obj = get_object_or_404(Order, pk=pk)
    printer_boot_obj = get_object_or_404(PrinterBoot, pk=ck)
   
    sustrate = None
    if printer_boot_obj.s_index >= 0:
        sustrate = Structure.objects.filter(plan__pk = order_obj.sale_order.plan.id )[printer_boot_obj.s_index]#type:ignore

    test_files = TestFile.objects.filter(boot_p=ck)
    result_cols_list = []
    bobbin_id_list = []

    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)
    
    for test in test_files:
        essays = TestFileEssay.objects.filter(test_file=test)
        if essays:
            results = TestFileEssayResult.objects.filter(essay=essays[0])
            result_cols_list.append(len(results))
            bobbin_id_list.append(results)
        else:
            result_cols_list.append(0)
            bobbin_id_list.append(0)

    content ='production/details/machine_boot.html'
    objects = zip(test_files, result_cols_list, bobbin_id_list)
    context = {
        'order_obj':order_obj,
        'printer_boot_obj':printer_boot_obj,
        'test_files':test_files,
        'objects':objects,
        'tab':'printer_boot',
        'sustrate':sustrate,
        'segment':'order',
        'detail':'production',
        'back': True,
        'content':content,
        'tab_p':printer_boot_obj.id, #type:ignore
        #render tabs--------------------
        'printer_boot':printer_boot,
        'laminator_boot':laminator_boot,
        'cutter_boot': cutter_boot,

    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)

#Laminator Boot------------------------------------------------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('production.add_printerboot', raise_exception=True)#type:ignore
@transaction.atomic
def OrderLaminatorBootAdd (request, pk):
    
    order_obj = get_object_or_404(Order, pk=pk)#Get the parent to render
    
    form = LaminatorBootForm(request.POST or None)
    formset_essay = LaminationEssayFormset(request.POST or None, prefix='essays')
    
    context = {'form': form, 'order_obj':order_obj, 'formset_essay':formset_essay, 'segment':'order', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid() and formset_essay.is_valid():
            laminator_boot = form.save(commit=False)
            laminator_boot.production_order = order_obj
            #validation            
            laminator_boot.save()

            eform = formset_essay.save(commit=False)
            for essay in eform:
                essay.laminator_boot = laminator_boot
                essay.result_p = average(essay.result_a, essay.result_b, essay.result_c, essay=essay)
                
                checks = [essay.check_a, essay.check_b, essay.check_c]
                results = [essay.result_a, essay.result_b, essay.result_c]
                valid_checks = [check for check, essay in zip(checks, results) if essay is not None and essay != '']
                essay.check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False #type:ignore
                #more validation
                essay.save() #type:ignore

            return redirect(f'/production/{order_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'production/forms/form-laminator_boot.html', context)

@login_required(login_url='/login/')
@permission_required('production.add_printerboot', raise_exception=True)#type:ignore
@transaction.atomic
def OrderLaminatorBootEdit (request, pk, ck):
    
    order_obj = get_object_or_404(Order, pk=pk)#Get the parent to render
    laminator_boot_obj = get_object_or_404(LaminatorBoot, pk=ck)

    form = LaminatorBootForm(request.POST or None, instance=laminator_boot_obj)
    formset_essay = LaminationEssayFormset(request.POST or None, prefix='essays', instance=laminator_boot_obj)
    
    context = {'form': form, 'formset_essay':formset_essay, 'order_obj':order_obj, 'laminator_boot_obj':laminator_boot_obj, 'segment':'order', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid() and formset_essay.is_valid():
            laminator_boot = form.save(commit=False)
            laminator_boot.production_order = order_obj
            laminator_boot.save(force_update=True)

            eform = formset_essay.save(commit=False)

            for edel in formset_essay.deleted_objects:
                edel.delete()

            for essay in eform:
                if not essay.id:
                    essay.laminator_boot = laminator_boot
                essay.result_p = average(essay.result_a, essay.result_b, essay.result_c, essay=essay)
                
                checks = [essay.check_a, essay.check_b, essay.check_c]
                results = [essay.result_a, essay.result_b, essay.result_c]
                valid_checks = [check for check, essay in zip(checks, results) if essay is not None and essay != '']
                essay.check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False #type:ignore
                
                #more validation
                essay.save() #type:ignore

            return redirect(f'/production/{order_obj.id}/laminator/{laminator_boot_obj.id}/') #type:ignore
        else:
            print(form.errors)
    return render(request, 'production/forms/form-laminator_boot.html', context)

@login_required(login_url='/login/')
@permission_required('production.delete_laminatorboot', raise_exception=True)
def OrderLaminatorBootDelete(request, pk):

    obj = get_object_or_404(LaminatorBoot, id=pk)
    order = obj.production_order.id#type:ignore

    if request.method == 'POST':
        obj.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))

    return redirect('order_details', order)

@login_required(login_url='/login/')
@permission_required('production.view_printerboot', raise_exception=True)
def OrderLaminatorBootDetails(request, pk, ck):
    
    order_obj = get_object_or_404(Order, pk=pk)
    laminator_boot_obj = get_object_or_404(LaminatorBoot, pk=ck)
    lamination_essay = LaminationEssay.objects.filter(laminator_boot=laminator_boot_obj).order_by('essay__priority')
    test_files = TestFile.objects.filter(boot_l=ck)
    result_cols_list = []
    bobbin_id_list = []
   
    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)

    for test in test_files:
        essays = TestFileEssay.objects.filter(test_file=test)
        if essays:
            results = TestFileEssayResult.objects.filter(essay=essays[0])
            result_cols_list.append(len(results))
            bobbin_id_list.append(results)
        else:
            result_cols_list.append(0)
            bobbin_id_list.append(0)
    
    objects = zip(test_files, result_cols_list, bobbin_id_list)
    content ='production/details/machine_boot.html'
    context = {
        'order_obj':order_obj,
        'laminator_boot_obj':laminator_boot_obj,
        'test_files':test_files,
        'objects':objects,
        'tab':'laminator_boot',
        'segment':'order',
        'detail':'production',
        'back': True,
        'content':content,
        'lamination_essay':lamination_essay,
        'tab_l':laminator_boot_obj.id, #type:ignore
        #render tabs--------------------
        'printer_boot':printer_boot,
        'laminator_boot':laminator_boot,
        'cutter_boot': cutter_boot,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)

#Unified Report CRUD------------------------------------------------------------------------>    
@login_required(login_url='/login/')
@permission_required('production.add_testfile', raise_exception=True)#type:ignore
@transaction.atomic
def ProductionReportAdd(request, pr, ck, machine):

    order_obj = get_object_or_404(Order, pk=pr)  # Get the parent to render
    if machine == 'laminator':
        boot_obj = get_object_or_404(LaminatorBoot, pk=ck)  # Get the parent to render
    elif machine == 'printer':
        boot_obj = get_object_or_404(PrinterBoot, pk=ck)  # Get the parent to render
    else:
        raise Http404("Invalid boot type")

    form = TestFileForm(request.POST or None)
    formset_essay = TestFileEssayFormset(request.POST or None, prefix='essays')
    formset_essay_result = TestFileEssayResultFormset(request.POST or None, prefix='results')

    formset = zip(formset_essay, formset_essay_result)
    essay_index = []

    context = {
        'form': form, 
        'formset': formset,
        'formset_essay': formset_essay,
        'formset_essay_result': formset_essay_result,
        'order_obj':order_obj,
        'boot_obj':boot_obj,
        'segment':'test_request',
        'back': True
    }

    if request.method == 'POST':
        
        if form.is_valid() and formset_essay.is_valid() and formset_essay_result.is_valid():
            test_file = form.save(commit=False)
            # validation
            if machine == 'laminator':
                test_file.boot_l = boot_obj
            elif machine == 'printer':
                test_file.boot_p = boot_obj

            if not request.user.has_perm('essays.supv_sign_testfile'):
                test_file.supervisor = None
            if not request.user.has_perm('essays.boss_sign_testfile'):
                test_file.boss = None
            test_file.save()
            bobbin = Bobbin.objects.create(test_file=test_file, turn=test_file.turn, date=test_file.date, quality_analist=test_file.quality_analist, production_operator=test_file.production_operator)

            essays = formset_essay.save(commit=False)
            eform = sorted(essays, key=lambda e: e.essay.priority)
            for essay in eform:
                essay.test_file = test_file                
                #more validation
                essay.save()

            rform = formset_essay_result.save(commit=False)
            for n, result in enumerate(rform):
                result.essay_id = essays[n].id
                result.bobbin = bobbin
                result.result_p = average(result.result_a, result.result_b, result.result_c, essay=result.essay)
                
                checks = [result.check_a, result.check_b, result.check_c]
                results = [result.result_a, result.result_b, result.result_c]
                valid_checks = [check for check, result in zip(checks, results) if result is not None and result != '']
                result.check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False #type:ignore
                #more validation
                result.save() #type:ignore
            
            return redirect(f'/production/{order_obj.id}/{machine}/{boot_obj.id}')  # type:ignore
        else:
            print(form.errors)
            print(formset_essay.errors)
            print(formset_essay_result.errors)
    return render(request, 'production/forms/form-test_file.html', context)

@login_required(login_url='/login/')
@permission_required('production.change_testfile', raise_exception=True)#type:ignore
def ProductionReportEdit(request, pr, ck, rp, machine):

    order_obj = get_object_or_404(Order, pk=pr)  # Get the parent to render
    if machine == 'laminator':
        boot_obj = get_object_or_404(LaminatorBoot, pk=ck)  # Get the parent to render
    elif machine == 'printer':
        boot_obj = get_object_or_404(PrinterBoot, pk=ck)  # Get the parent to render
    else:
        raise Http404("Invalid boot type")

    test_file_obj = get_object_or_404(TestFile, pk=rp)
    form = TestFileForm(request.POST or None, instance=test_file_obj)

    context = {
        'form': form, 
        'order_obj': order_obj,
        'boot_obj': boot_obj,
        'segment': 'test_request',
        'back': True
    }

    if request.method == 'POST':
        if form.is_valid():
            test_file = form.save(commit=False)
            # validation
            if not request.user.has_perm('essays.supv_sign_testfile'):
                test_file.supervisor = test_file_obj.supervisor or None
            if not request.user.has_perm('essays.boss_sign_testfile'):
                test_file.boss = test_file_obj.boss or None
            test_file.save()

            return redirect(f'/production/{order_obj.id}/{machine}/{boot_obj.id}')  # type:ignore
        else:
            print(form.errors)
    return render(request, 'production/forms/form-test_file.html', context)

@login_required(login_url='/login/')
@permission_required('production.delete_testfile', raise_exception=True)#type:ignore
def ProductionReportDelete(request, pr, ck, rp, machine):
    report = get_object_or_404(TestFile, pk=rp)
    if request.method == 'POST':
        report.delete()
    return redirect(f'/production/{pr}/{machine}/{ck}')

#Bobbins and Essays 
@login_required(login_url='/login/')
@permission_required('production.add_testfileessayresult', raise_exception=True)#type:ignore
@transaction.atomic
def ReportBobbinAdd (request, tr, ck, tf, machine):

    order_obj = get_object_or_404(Order, pk=tr)#Get the grandparent to render

    analyst = QualityAnalyst.objects.filter(active=True).order_by('name')
    operator = ProductionOperator.objects.filter(active=True).order_by('name')

    test_file = get_object_or_404(TestFile, pk=tf)
    essays = TestFileEssay.objects.filter(test_file__pk=tf).order_by('essay__priority')
    curr_bobbin = len(TestFileEssayResult.objects.filter(essay=essays[0])) + 1
    FromsetResults = modelformset_factory(TestFileEssayResult, fields='__all__', extra=len(essays))

    if request.method == 'POST':
        formset = FromsetResults(request.POST, prefix='results')
        if formset.is_valid():
            data = request.POST

            raw_date = datetime.datetime.strptime(data['date'], "%d/%m/%Y")
            date = raw_date.strftime("%Y-%m-%d")

            analyst_o = QualityAnalyst.objects.get(id=data['quality_analist'])
            operator_o = ProductionOperator.objects.get(id=data['production_operator'])

            bobbin = Bobbin.objects.create(test_file=test_file, turn=data['turn'], date=date, quality_analist=analyst_o, production_operator=operator_o)

            rform = formset.save(commit=False)
            for result in rform:                
                result.bobbin = bobbin
                result.result_p = average(result.result_a, result.result_b, result.result_c, essay=result.essay)
                
                checks = [result.check_a, result.check_b, result.check_c]
                results = [result.result_a, result.result_b, result.result_c]
                valid_checks = [check for check, result in zip(checks, results) if result is not None and result != '']
                result.check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False  #type:ignore
                #more validation
                result.save() #type:ignore

            
            return redirect(f'/production/{tr}/{machine}/{ck}')
        else:
            print(formset.errors)
    else:
        formset = FromsetResults(queryset=TestFileEssayResult.objects.none(), prefix='results')
    context = {
        'formset': formset,
        'essays': essays,
        'curr_bobbin': curr_bobbin,
        'order_obj':order_obj,
        'analyst':analyst,
        'operator':operator,
        'segment':'order',
        'back': True
    }

    return render(request, 'production/forms/form-report_bobbin_add.html', context)

@login_required(login_url='/login/')
@permission_required('production.delete_bobbin', raise_exception=True)#type:ignore
def ReportBobbinDelete (request, pk):
    obj = Bobbin.objects.get(id=pk)
    obj.delete()
    return JsonResponse({'success': True})

#Essay
@login_required(login_url='/login/')
@permission_required('production.add_testfileessay', raise_exception=True)#type:ignore
@transaction.atomic
def ReportEssayAdd (request, pk, op, machine, ck):
    
    test_file = TestFile.objects.get(pk=pk)
    results = []
    
    essays = TestFileEssay.objects.filter(test_file=test_file)
    if essays:
        results = TestFileEssayResult.objects.filter(essay=essays[0])
    else:
        results.append('na')

    form = TestFileEssayForm(request.POST or None)
    formset = TestFileEssayResultFormset(request.POST or None, queryset=TestFileEssayResult.objects.none(), prefix='results')

    context = {'form': form, 'formset': formset, 'order_obj':Order.objects.get(pk=op), 'results': results, 'result_total': len(results), 'segment':'order', 'back': True}

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            essay = form.save(commit=False)
            essay.test_file = test_file
            #validation
            essay.save()

            forms = formset.save(commit=False)

            for n, res in enumerate(forms):
                res.essay = essay
                bobbin_id = request.POST.get('actual-' + str(n) + '-bobbin') or None
                if not bobbin_id:
                    res.bobbin = Bobbin.objects.create(test_file=test_file, turn=test_file.turn, date=test_file.date, quality_analist=test_file.quality_analist, production_operator=test_file.production_operator)
                else:
                    bobbin = Bobbin.objects.filter(pk=bobbin_id).first()
                    res.bobbin = bobbin
                res.result_p = average(res.result_a, res.result_b, res.result_c, essay=res.essay) 
                
                checks = [res.check_a, res.check_b, res.check_c]
                results = [res.result_a, res.result_b, res.result_c]
                valid_checks = [check for check, res in zip(checks, results) if res is not None and res != '']
                res.check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False #type:ignore
                res.save()  #type:ignore

            return redirect(f'/production/{op}/{machine}/{ck}')
        else:
            print(form.errors)
            print(formset.errors)
    return render(request, 'production/forms/form-essay_add.html', context)

@login_required(login_url='/login/')
@permission_required('production.change_testfileessay', raise_exception=True)#type:ignore
@transaction.atomic
def ReportEssayEdit (request, pk, op, machine, ck):
    
    obj = get_object_or_404(TestFileEssay, pk=pk)

    form = TestFileEssayForm(request.POST or None, instance=obj)
    formset = TestFileEssayResultFormset(request.POST or None, prefix='results', instance = obj)

    context = {'form': form,'formset': formset, 'segment':'order', 'set': 'edit', 'back': True}

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            essay = form.save(commit=False)
            #validation
            essay.save(force_update=True)

            forms = formset.save(commit=False)

            for rms in formset.deleted_objects:
                rms.delete()
            
            for res in forms:
                res.result_p = average(res.result_a, res.result_b, res.result_c, essay=res.essay)

                checks = [res.check_a, res.check_b, res.check_c]
                results = [res.result_a, res.result_b, res.result_c]
                valid_checks = [check for check, res in zip(checks, results) if res is not None and res != '']
                res.check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False #type:ignore
                res.save(force_update=True)  #type:ignore

            return redirect(f'/production/{op}/{machine}/{ck}')

        else:
            print(formset.errors)
    return render(request, 'production/forms/form-essay_edit.html', context)

@login_required(login_url='/login/')
@permission_required('production.delete_testfileessay', raise_exception=True)#type:ignore
def ReportEssayDelete (request, pk):
    obj = TestFileEssay.objects.get(id=pk)
    obj.delete()
    return JsonResponse({'success': True})

#Cutter Boot------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('production.add_cutterboot', raise_exception=True)#type:ignore
def OrderCutterBootAdd (request, pk):
    
    order_obj = get_object_or_404(Order, pk=pk)#Get the parent to render

    structure_list = Structure.objects.filter(plan__pk=order_obj.sale_order.plan.id)#type: ignore
    tr_weight = 0
    for st in structure_list:
        tr_weight = tr_weight + st.weight #type:ignore

    form = CutterBootForm(request.POST or None)
    context = {'form': form, 'order_obj':order_obj, 'tr_weight':tr_weight, 'segment':'order', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            cutter_boot = form.save(commit=False)
            #validation
            cutter_boot.r_p = average(cutter_boot.r_a, cutter_boot.r_b, cutter_boot.r_c)
            cutter_boot.w_p = average(cutter_boot.w_a, cutter_boot.w_b, cutter_boot.w_c)
            cutter_boot.production_order = order_obj
            cutter_boot.save()

            order_obj.save()
                
            return redirect(f'/production/{pk}')
        else:
            print(form.errors)
    return render(request, 'production/forms/form-cutter_boot.html', context)

@login_required(login_url='/login/')
@permission_required('production.change_cutterboot', raise_exception=True)#type:ignore
def OrderCutterBootEdit (request, pk, ck):
    order_obj = get_object_or_404(Order, pk=pk)#Get the parent to render
    cutter_boot_obj = get_object_or_404(CutterBoot, pk=ck)

    structure_list = Structure.objects.filter(plan__pk=order_obj.sale_order.plan.id) #type:ignore
    tr_weight = 0
    for st in structure_list:
        tr_weight = tr_weight + st.weight #type:ignore

    form = CutterBootForm(request.POST or None, instance=cutter_boot_obj)
    context = {'form': form, 'order_obj':order_obj, 'tr_weight':tr_weight, 'segment':'order', 'detail':'production', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            cutter_boot = form.save(commit=False)
            #validation
            cutter_boot.r_p = average(cutter_boot.r_a, cutter_boot.r_b, cutter_boot.r_c)
            cutter_boot.w_p = average(cutter_boot.w_a, cutter_boot.w_b, cutter_boot.w_c)
            cutter_boot.production_order = order_obj
            cutter_boot.save()

            order_obj.save()
                
            return redirect(f'/production/{pk}/cutter/{ck}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'production/forms/form-cutter_boot.html', context)

@login_required(login_url='/login/')
@permission_required('production.delete_cutterboot', raise_exception=True)#type:ignore
def OrderCutterBootDelete (request, pk):
    item = get_object_or_404(CutterBoot, pk=pk)
    if request.method == 'POST':
        item.delete()
    return redirect(f'/production/{item.production_order.id}')#type: ignore

@login_required(login_url='/login/')
@permission_required('production.view_cutterboot', raise_exception=True)
def OrderCutterBootDetails(request, pk, ck):
    
    order_obj = get_object_or_404(Order, pk=pk)#Get the parent to render

    structure_list = Structure.objects.filter(plan__pk=order_obj.sale_order.plan.id)#type: ignore
    tr_weight = 0
    for st in structure_list:
        tr_weight = tr_weight + st.weight #type:ignore
    cutter_boot_obj = get_object_or_404(CutterBoot, pk=ck)
    
    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)

    content ='production/details/cutter_boot.html'

    context = {
        'order_obj':order_obj,
        'cutter_boot_obj':cutter_boot_obj,
        'tr_weight':tr_weight,
        'segment':'order',
        'detail':'production',
        'tab_c':cutter_boot_obj.id, #type: ignore
        'back': True,
        'content':content,
        'printer_boot':printer_boot,
        'laminator_boot':laminator_boot,
        'cutter_boot':cutter_boot,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)
#TechSpecs---------------------------------------------------------------------------------------------->

@login_required(login_url='/login/')
@permission_required('essays.add_technicalspecs', raise_exception=True)#type:ignore
def OrderTechSpecsAdd (request, pk):
    order_obj = get_object_or_404(Order, pk=pk)

    form = TechnicalSpecsForm(request.POST or None)
    formset = DispatchFormset(request.POST or None, prefix='adresses')
    context = {'form': form, 'formset': formset, 'order_obj': order_obj, 'segment':'order', 'back': True}
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            techspec = form.save(commit=False)
            techspec.production_order = order_obj
            techspec.save()
            addresses = formset.save(commit=False)
            for addrs in addresses:
                addrs.technical_specs = techspec
                
                addrs.save()
            
            
        else:
            print(form.errors)
        return redirect(f'/production/{pk}/techspecs')
    return render(request, 'production/forms/form-technical_specs.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_technicalspecs', raise_exception=True)#type:ignore
def OrderTechSpecsEdit (request, pk, ck):
    order_obj = get_object_or_404(Order, pk=pk)

    tech_specs_obj = get_object_or_404(TechnicalSpecs, pk=ck)
    form = TechnicalSpecsForm(request.POST or None, instance=tech_specs_obj)
    formset = DispatchFormset(request.POST or None, prefix='adresses', instance=tech_specs_obj)
    context = {'form': form, 'formset': formset, 'order_obj': order_obj, 'segment':'test_request', 'back': True}
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            techspecs = form.save()

            dispatches = formset.save(commit=False)
            
            for rms in formset.deleted_objects:
                rms.delete()

            for dp in dispatches:
                if not dp.technical_specs:
                    dp.technical_specs = techspecs
                
                dp.save()
        else:
            print(form.errors)

        return redirect(f'/production/{pk}/techspecs')

    return render(request, 'production/forms/form-technical_specs.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_technicalspecs', raise_exception=True)#type:ignore
def OrderTechSpecsDelete (request, tr, ck):
    item = get_object_or_404(TechnicalSpecs, pk=ck)
    if request.method == 'POST':
        item.delete()
        return redirect('view_test_request', tr)
    
    return render(request, 'essays/form-annex.html')

@login_required(login_url='/login/')
@permission_required('essays.view_technicalspecs', raise_exception=True)
def OrderTechSpecsDetails(request, pk):
    
    order_obj = get_object_or_404(Order, pk=pk)
   
    structure_list = Structure.objects.filter(plan=order_obj.sale_order.plan)#type: ignore

    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)

    latest_lam = None
    latest_report = None
    latest_cutter = None

    if laminator_boot:
        latest_lam = laminator_boot.latest('id')
        reports = TestFile.objects.filter(boot_l__id=latest_lam.pk)
        latest_report = reports.last()
    elif printer_boot:
        latest_lam = printer_boot.latest('id')
        reports = TestFile.objects.filter(boot_p__id=latest_lam.pk)
        latest_report = reports.last()

    if cutter_boot:
        latest_cutter = cutter_boot.latest('id')

    all_delal = TestFileEssay.objects.filter(test_file__boot_l__production_order=order_obj).filter(essay__method="011").order_by('test_file__boot_l__step')

    annexes = Annex.objects.filter(production_order__pk=pk)

    content = 'production/details/tech_specs.html'
    
    context = {
        'order_obj':order_obj,
        'structure_list':structure_list,
        'printer_boot':printer_boot,
        'laminator_boot':laminator_boot,
        'latest_lam':latest_lam,
        'latest_report':latest_report,
        'all_delal':all_delal,
        'cutter_boot':cutter_boot,
        'latest_cutter':latest_cutter,
        'tab_ts':True,
        'annexes':annexes,
        'segment':'order',
        'detail':'production',
        'tab':'tech_specs',
        'back': True,
        'content':content
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)

#Annex-------------------------------------------------------------------------------------------------->
@login_required(login_url="/login/")
@permission_required('production.view_annex', raise_exception=True)
def OrderAnnexes(request, pk):
    order_obj = get_object_or_404(Order, pk=pk)
    printer_boot = PrinterBoot.objects.filter(production_order__pk=pk)
    laminator_boot = LaminatorBoot.objects.filter(production_order__pk=pk)
    cutter_boot = CutterBoot.objects.filter(production_order__pk=pk)

    annexes = Annex.objects.filter(production_order__pk=pk)
    content = 'production/details/annexes.html'
    
    context = {
        'order_obj': order_obj,
        'printer_boot': printer_boot,
        'laminator_boot': laminator_boot,
        'cutter_boot': cutter_boot,
        'annexes': annexes,
        'content': content,
        'segment': 'order',
        'tab': 'annex',
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'production/details-production.html', context)

@login_required(login_url='/login/')
@permission_required('essays.add_annex', raise_exception=True)#type:ignore
def OrderAnnexAdd(request, pk):
    order_obj = get_object_or_404(Order, pk=pk)
    number = "0"
    last_annex = Annex.objects.last()
    if last_annex:
        number = get_the_num(last_annex.image.name)
    context = {'order_obj': order_obj, 'segment':'order', 'back': True}
    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')

        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            context['message'] = 'Sólo se admiten imágenes en formato JPG o PNG'
            return render(request, 'production/forms/form-annex.html', context)

        image.name = rename_file(image.name, number)

        try:
            img = Image.open(image)
            img = ImageOps.exif_transpose(img)

            if isinstance(img, JpegImagePlugin.JpegImageFile):
                img.info.pop('exif', None)
        except IOError:
            context['message'] = 'El archivo no es una imagen válida o está dañado'
            return render(request, 'production/forms/form-annex.html', context)

        max_size = (2000, 2000)
        img.thumbnail(max_size)#type: ignore

        output = BytesIO()
        img = img.convert("RGB")#type: ignore
        img.save(output, format='JPEG', quality=30)

        output.seek(0)

        image = File(output, name=image.name)

        Annex.objects.create(
            production_order=order_obj,
            identification=data['identification'],
            image=image,
            )
        
        return redirect('production_annexes', pk)
    
    return render(request, 'production/forms/form-annex.html', context)

def rename_file(name, id):
    extension = name.split('.')[-1]
    name = str(id).zfill(8) + '.' + extension
    return (name)

def get_the_num(val):
    num = re.findall(r'\d+', val)
    if num:
        return int(num[0]) + 1
    else:
        return "No se encontró ningún número en la cadena."
    
@login_required(login_url='/login/')
@permission_required('essays.delete_annex', raise_exception=True)#type:ignore
def OrderAnnexDelete (request, pk, ck):
    obj = get_object_or_404(Annex, pk=ck)
    if request.method == 'POST':
        obj.delete()
    return redirect('production_annexes', pk)

login_required(login_url='/login/')
@permission_required('essays.export_boot', raise_exception=True)#type:ignore
@transaction.atomic
def ExportBoot(request, pk, machine, ck):
    
    if request.method == 'POST':
        parent = get_object_or_404(Order, pk=pk)

        destiny_type, destiny_id = request.POST.get('destiny_document').split('-')
        if destiny_type == 'OP':
            destiny_document = get_object_or_404(Order, pk=destiny_id)
            address = 'production'
        elif destiny_type == 'PR':
            destiny_document = get_object_or_404(ArtRequest, pk=destiny_id)
            address = 'test_requests'

        if destiny_type == 'OP':
            model_mapping = {
                'PrinterBoot': PrinterBoot,
                'LaminatorBoot': LaminatorBoot,
                'TestFile': TestFile,
                'TestFileEssay': TestFileEssay,
                'TestFileEssayResult': TestFileEssayResult,
                'Bobbin': Bobbin,
            }

        elif destiny_type == 'PR':
            model_mapping = {
                'PrinterBoot': EssaysPrinterBoot,
                'LaminatorBoot': EssaysLaminatorBoot,
                'LaminationEssay': EssaysLaminationEssay,
                'TestFile': EssaysTestFile,
                'TestFileEssay': EssaysTestFileEssay,
                'TestFileEssayResult': EssaysTestFileEssayResult,
                'Bobbin': EssaysBobbin,
            }

        machine_types = {'printer': PrinterBoot,'laminator': LaminatorBoot}
        
        if machine in machine_types:
            og_boot = get_object_or_404(machine_types[machine], pk=ck)
            og_boot_id = og_boot.id
        else:
            return HttpResponseBadRequest(request)

        data = og_boot.__dict__
        del data['_state'] 
        del data['id'] 
        del data['production_order_id']

        if not data['origin']:
            data['origin'] = f'OP-{parent.number}'

        if destiny_type == 'OP':
            data['production_order_id'] = destiny_id

        elif destiny_type == 'PR':
            data['test_request_id'] = destiny_id

            if machine == 'printer':
                del data['s_index']
                del data['provider']
                del data['sustrate_width']

        if machine == 'printer':
            boot = model_mapping['PrinterBoot'](**data)
        elif machine == 'laminator':
            boot = model_mapping['LaminatorBoot'](**data)
            
        boot.save()
        
        for related_object in machine_types[machine].objects.get(id=og_boot_id)._meta.related_objects:
            if related_object.one_to_many and related_object.field.name not in ['production_operator', 'quality_analist']:
                for obj in getattr(machine_types[machine].objects.get(id=og_boot_id), related_object.get_accessor_name()).all():
                    obj_data = deepcopy(obj)
                    data_2 = obj_data.__dict__
                    del data_2['_state']
                    del data_2['_django_version']
                    del data_2['id']
                    data_2[f'{related_object.field.name}_id'] = boot.id

                    if 'laminator_boot_id' in data_2:
                        obj_copy = model_mapping['LaminationEssay'](**data_2)
                        obj_copy.save()
                    else:
                        obj_copy = model_mapping['TestFile'](**data_2)
                        obj_copy.save()

                    # Check for TestFile objects and copy associated Bobbin and TestFileEssay objects
                    if isinstance(obj_copy, model_mapping['TestFile']):
                        bobbin_dict = {}
                        for n, bobbin in enumerate(Bobbin.objects.filter(test_file=obj)):
                            bobbin_data = deepcopy(bobbin)
                            data_3 = bobbin_data.__dict__

                            del data_3['_state']
                            del data_3['_django_version']
                            del data_3['id']
                            data_3['test_file_id'] = obj_copy.id

                            bobbin_copy = model_mapping['Bobbin'](**data_3)
                            bobbin_copy.save()
                            bobbin_dict[n] = bobbin_copy.id
                        
                        for testfileessay in TestFileEssay.objects.filter(test_file=obj):
                            testfileessay_data = deepcopy(testfileessay)
                            data_4 = testfileessay_data.__dict__

                            del data_4['_state']
                            del data_4['_django_version']
                            del data_4['id']
                            data_4['test_file_id'] = obj_copy.id

                            testfileessay_copy = model_mapping['TestFileEssay'](**data_4)
                            testfileessay_copy.save()

                            # Copy associated TestFileEssayResult objects
                            for n, result in enumerate(TestFileEssayResult.objects.filter(essay=testfileessay)):
                                result_data = deepcopy(result)
                                data_5 = result_data.__dict__
                                del data_5['_state']
                                del data_5['_django_version']
                                del data_5['id']
                                data_5['essay_id'] = testfileessay_copy.id
                                data_5['bobbin_id'] = bobbin_dict[n]

                                result_copy = model_mapping['TestFileEssayResult'](**data_5)
                                result_copy.save()

        return redirect(f'/{address}/{destiny_document.id}/{machine}/{boot.id}')#type: ignore
    
    return HttpResponseBadRequest