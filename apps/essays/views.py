from email import header
import datetime, re
from io import BytesIO
from urllib import request
from unittest import result
from PIL import Image, ImageOps, JpegImagePlugin
Image.MAX_IMAGE_PIXELS = 999999999 
from copy import deepcopy
from django.db import transaction, connection 
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, Http404
from django.utils import timezone
from django.core import serializers
from django.forms import modelformset_factory
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files import File
from django.test.utils import CaptureQueriesContext
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from apps.authentication.views import compiled_data

#app imports------------------------------------------------------->
from .filters import *
from .forms import *
from .models import *
from apps.production.models import Order, PrinterBoot as ProductionPrinterBoot, LaminatorBoot as ProductionLaminatorBoot, LaminationEssay as ProductionLaminationEssay, TestFile as ProductionTestFile,  TestFileEssay as ProductionTestFileEssay,  TestFileEssayResult as ProductionTestFileEssayResult, Bobbin as ProductionBobbin
from apps.home.views import get_id
#from .utils import *

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

def test_case(request):
    result = request
    test_data = compiled_data(request)
    if test_data == None:
        result = None
    return result
#-----------------------------------------------------------------------------------------
#Esto lista los elementos de entrada de una solicitud de ensayo
#Ademas de manejar el estado de las entradas en la tabla (eliminado editado o aprobado [Parece no estarse usando esto ultimo])
class indexEntryElement(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    permission_required = 'essays.view_entryelement'
    model = EntryElement
    template_name = 'essays/tables-test_request.html'
    ordering = ['-date']
    context_object_name = 'objects'
    paginate_by = 15
    orphans = 2

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Elementos de Entrada'
        context['segment'] = 'requests'
        context['tab'] = 'entry'
        context['search'] = True
        context['table'] = 'essays/tables/entry_element.html'
       
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_text = self.request.GET.get('search_text', None)
        if search_text:
            queryset = queryset.filter(
                Q(product__icontains=search_text)|
                Q(client__name__icontains=search_text)|
                Q(test_client__icontains=search_text)|
                Q(date__icontains=search_text)
            )
        
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table_html = render_to_string('essays/tables/entry_element.html', context, request=self.request)
            paginator_html = render_to_string('essays/paginators/obj.html', context, request=self.request)
            return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        else:
            return super().render_to_response(context, **response_kwargs)

@login_required(login_url='/login/')
@permission_required('essays.add_entryelement', raise_exception=True)
def addEntryElement(request):
    if request.method == 'POST':
        form = EntryElementForm(request.POST, request.FILES)
        if form.is_valid():
            ee = form.save()

            tr_id = request.POST.get('test_request')
            if tr_id:
                try:
                    tr = TestRequest.objects.get(pk=tr_id)
                    tr.entry_element = ee
                    tr.save()  
                except TestRequest.DoesNotExist:
                    pass

            response_data = {
                'success': True,
                'url': '/entry_elements/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            response_data = {
                'success': False,
                'form_errors': errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = EntryElementForm()
        context ={
            'form':form,
            'segment':'requests',
            'back':True
        }
        return render(request, 'essays/form-entry_element.html', context)
    

@login_required(login_url='/login/')
@permission_required('essays.change_entryelement', raise_exception=True)
def editEntryElement(request, pk):

    obj = get_object_or_404(EntryElement, pk=pk)

    lock = None
    if obj.has_test_request:
        lock = obj
        
    try:
        tr = TestRequest.objects.get(entry_element__pk=obj.pk)
        selected_tr = f'<option value="{tr.pk}" selected>{tr.number} - {tr.product}</option>'
    except:
        tr = None
        selected_tr = ''

    if request.method == 'POST':
        form = EntryElementForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            ee = form.save()

            tr_id = request.POST.get('test_request')
            if tr_id:
                try:
                    tr = TestRequest.objects.get(pk=tr_id)
                    tr.entry_element = ee
                    tr.save()  
                except TestRequest.DoesNotExist:
                    pass

            response_data = {
                'success': True,
                'url': '/entry_elements/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            response_data = {
                'success': False,
                'form_errors': errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = EntryElementForm(instance=obj)
        context ={
            'object':obj,
            'form':form,
            'selected_tr':selected_tr,
            'test_request_obj':tr,
            'segment':'requests',
            'back':True,
            'lock':lock
        }
        return render(request, 'essays/form-entry_element.html', context)
    

@login_required(login_url='/login/')
@permission_required('essays.add_entryelement', raise_exception=True)
def deleteEntryElement(request, pk):

    obj = get_object_or_404(EntryElement, pk=pk)

    if request.method == 'POST':
        obj.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
        return redirect('test_request')

    return render(request, 'essays/form-entry_element.html')
#-----------------------------------------------------------------------------------------
#Esto lista los elementos de entrada de una solicitud de ensayo de arte
class indexEntryElementArt(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    permission_required = 'essays.view_artentryelement'
    model = ArtEntryElement
    template_name = 'essays/tables-test_request_art.html'
    ordering = ['-date']
    context_object_name = 'objects'
    paginate_by = 15
    orphans = 2

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        
        context = self.get_context_data()
        return self.render_to_response(context)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Elementos de Entrada de Arte'
        context['segment'] = 'requests_art'
        context['tab'] = 'art_entry'
        context['search'] = True
        context['table'] = 'essays/tables/entry_element_art.html'
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_text = self.request.GET.get('search_text', None)
        if search_text:
            queryset = queryset.filter(
                Q(product__icontains=search_text)|
                Q(client__name__icontains=search_text)|
                Q(test_client__icontains=search_text)|
                Q(date__icontains=search_text)
            )
        return queryset
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table_html = render_to_string('essays/tables/entry_element_art.html', context, request=self.request)
            paginator_html = render_to_string('essays/paginators/obj.html', context, request=self.request)
            return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        else:
            return super().render_to_response(context, **response_kwargs)

@login_required(login_url='/login/')
@permission_required('essays.add_artentryelement', raise_exception=True)
def addEntryElementArt(request):
    if request.method == 'POST':
        form = ArtEntryElementForm(request.POST, request.FILES)
        if form.is_valid():
            ee = form.save()

            tr_id = request.POST.get('art_request')
            if tr_id:
                try:
                    tr = ArtRequest.objects.get(pk=tr_id)
                    tr.entry_element = ee
                    tr.save()  
                except ArtRequest.DoesNotExist:
                    pass

            response_data = {
                'success': True,
                'url': '/entry_elements_art/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            response_data = {
                'success': False,
                'form_errors': errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = ArtEntryElementForm()
        context ={
            'form':form,
            'segment':'requests_art',
            'back':True
        }
        return render(request, 'essays/form-entry_element_art.html', context)

#-----------------------------------------------------------------------------------------
#Esto lista los elementos de salida de una solicitud de ensayo
#Ademas de manejar el estado de las entradas en la tabla (eliminado editado o aprobado [Parece no estarse usando esto ultimo])
class indexExitElement(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    permission_required = 'essays.view_exitelement'
    model = ExitElement
    template_name = 'essays/tables-test_request.html'
    ordering = ['-test_request__production_order']
    context_object_name = 'objects'
    paginate_by = 15
    orphans = 2

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Elementos de Entrada'
        context['segment'] = 'requests'
        context['tab'] = 'exit'
        context['search'] = True
        context['table'] = 'essays/tables/exit_element.html'
       
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_text = self.request.GET.get('search_text', None)
        if search_text:
            queryset = queryset.filter(
                #Q(product__icontains=search_text)|
                #Q(client__name__icontains=search_text)|
                #Q(test_client__icontains=search_text)|
                #Q(date__icontains=search_text)
            )
        
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table_html = render_to_string('essays/tables/exit_element.html', context, request=self.request)
            paginator_html = render_to_string('essays/paginators/obj.html', context, request=self.request)
            return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        else:
            return super().render_to_response(context, **response_kwargs)
        
@login_required(login_url='/login/')
@permission_required('essays.add_entryelement', raise_exception=True)
def addExitElement(request, tr):
    try:
        test_request_obj = TestRequest.objects.get(pk=tr)
    except:
        raise Http404
    
    if request.method == 'POST':
        form = ExitElementForm(request.POST, request.FILES)
        if form.is_valid():

            ee = form.save(commit=False)
            ee.test_request = test_request_obj
            if ee.shelf_life == 'eva':
                ee.shelf_life_date = timezone.now()
            ee.save()

            response_data = {
                'success': True,
                'url': f'/test_requests/{tr}/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            response_data = {
                'success': False,
                'form_errors': errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = ExitElementForm()
        context ={
            'form':form,
            'segment':'requests',
            'test_request_obj':test_request_obj,
            'back':True
            }
        return render(request, 'essays/form-exit_element.html', context)
@login_required(login_url='/login/')
@permission_required('essays.add_exitelement', raise_exception=True)
def editExitElement(request, pk):
    
    obj = ExitElement.objects.get(pk=pk)
    shelf = obj.shelf_life
    if request.method == 'POST':
        form = ExitElementForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            ee = form.save(commit=False)

            print(ee.shelf_life, shelf)
            if ee.shelf_life == 'eva' and ee.shelf_life != shelf:
                print('entro')
                ee.shelf_life_date = timezone.now()

            ee.save()
            response_data = {
                'success': True,
                'url': f'/test_requests/{obj.test_request.id}/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            response_data = {
                'success': False,
                'form_errors': errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = ExitElementForm(instance=obj)
        context ={
            'object':obj,
            'form':form,
            'test_request_obj':obj.test_request,
            'segment':'requests',
            'back':True
            }
        return render(request, 'essays/form-exit_element.html', context)


@login_required(login_url='/login/')
@permission_required('essays.delete_exitelement', raise_exception=True)
def deleteExitElement(request, pk):

    obj = get_object_or_404(ExitElement, pk=pk)

    if request.method == 'POST':
        obj.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
        return redirect('test_request')

    return render(request, 'essays/form-exit_element.html')

#-----------------------------------------------------------------------------------------

@login_required(login_url="/login/")
@permission_required('essays.view_testrequest', raise_exception=True)
def ajaxTestRequest(request):
    filtr = request.GET.get('f', None)

    test_requests = TestRequest.objects.exclude(Q(deleted=True)|Q(number=None)).order_by('-number')
    if request.GET.get('exclude_ee'):
        test_requests = test_requests.filter(entry_element=None)
    if filtr:
        test_requests = test_requests.filter(Q(number__icontains=filtr)|Q(product__icontains=filtr)).only("pk", "number", "product", "date")

    tr_list = serializers.serialize('json', test_requests)#type: ignore
    #tr_list = list(test_requests)
    return JsonResponse(tr_list, safe=False)
    
@login_required(login_url="/login/")
@permission_required('essays.view_testrequest', raise_exception=True)
def indexTestRequest(request):

    header = request.GET.get('header') or request.session.get('header')
    if header == "deleted":
        test_request_obj = TestRequest.objects.filter(deleted=True).order_by('-number')
        tab = 'deleted'
    elif header == "archived":
        test_request_obj = TestRequest.objects.filter(archived=True).order_by('-number')
        tab = 'archived'
    elif header == "review":
        test_request_obj = TestRequest.objects.exclude(Q(deleted=True)|Q(archived=True)|Q(closed=True)).filter(reviewer=None).order_by('-number')
        tab = 'review'
    elif request.GET.get('touched') != 'closed':
        test_request_obj = TestRequest.objects.exclude(Q(deleted=True)|Q(archived=True)|Q(closed=True)).exclude(reviewer=None).order_by('-number')
        tab = 'main'
        segment = 'request'
    
    if request.session.get('header'):
        request.session['header'] = None

    touched = request.GET.get('touched')
    if touched:
        if touched != 'closed':
            val = touched == 'True'
            if val == False:
                #solicitud
                segment = 'requests'
                order = '-number'
            else:
                #expedientes
                segment = 'test_request'
                order = '-production_order'

            test_request_obj = test_request_obj.filter(Q(touched=val)).order_by(order)
        else:
            tab = 'main'
            segment = 'closed_test_request'
            order = '-production_order'

            test_request_obj = TestRequest.objects.filter(Q(closed=True)).order_by(order)

    else:
        segment = 'requests'
        test_request_obj = test_request_obj.filter(Q(touched=False))

    search_text = request.GET.get('search_text')
    if search_text:
        test_request_obj = test_request_obj.filter(
            Q(product__icontains=search_text)|
            Q(number__icontains=search_text)|
            Q(production_order__icontains=search_text)|
            Q(client__name__icontains=search_text)|
            Q(test_client__icontains=search_text)
        )

    test_request_filter = TestRequestFilter(request.GET, queryset=test_request_obj)
    test_request_obj = test_request_filter.qs
        
    paginator = Paginator(test_request_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    test_request_list = paginator.get_page(page_number)

    context={
        'objects':test_request_list,
        'test_request_filter':test_request_filter,
        'segment': segment,
        'table': 'essays/tables/test_request.html',
        'search': True,
        'tab':tab
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('essays/tables/test_request.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'essays/tables-test_request.html', context)


#-----------------------------------------------------------------------------------------
#lista las solicitudes de ensayo de arte
@login_required(login_url="/login/")
@permission_required('essays.view_artrequest', raise_exception=True)
def indexTestRequestArt(request):

    header = request.GET.get('header') or request.session.get('header')
    if header == "deleted":
        art_request_obj = ArtRequest.objects.filter(deleted=True).order_by('-number')
        tab = 'deleted'
    elif header == "archived":
        art_request_obj = ArtRequest.objects.filter(archived=True).order_by('-number')
        tab = 'archived'
    elif header == "review":
        art_request_obj = ArtRequest.objects.exclude(Q(deleted=True)|Q(archived=True)|Q(closed=True)).filter(reviewer=None).order_by('-number')
        tab = 'review'
        #Lista general de las solicitudes
    elif request.GET.get('touched') != 'closed':
        art_request_obj = ArtRequest.objects.exclude(Q(deleted=True)|Q(archived=True)|Q(closed=True)).exclude(reviewer=None).order_by('-number')
        tab = 'main'
        segment = 'requests_art'
 #       print(art_request_obj.query)
  #      print(segment)
   #     print(art_request_obj)

    
    if request.session.get('header'):
        request.session['header'] = None

    touched = request.GET.get('touched')
    if touched:
        if touched != 'closed':
            val = touched == 'True'
            if val == False:
                #solicitud
                segment = 'requests_art'
                order = '-number'
            else:
                #expedientes
                segment = 'art_request'
                order = '-production_order'

            art_request_obj = art_request_obj.filter(Q(touched=val)).order_by(order)
        else:
            tab = 'main'
            segment = 'closed_art_request'
            order = '-production_order'

            art_request_obj = ArtRequest.objects.filter(Q(closed=True)).order_by(order)

    else:
        segment = 'requests_art'
        art_request_obj = art_request_obj.filter(Q(touched=False))

    search_text = request.GET.get('search_text')
    if search_text:
        art_request_obj = art_request_obj.filter(
            Q(product__icontains=search_text)|
            Q(number__icontains=search_text)|
            Q(production_order__icontains=search_text)|
            Q(client__name__icontains=search_text)|
            Q(test_client__icontains=search_text)
        )

    art_request_filter = TestRequestFilter(request.GET, queryset=art_request_obj)
    art_request_obj = art_request_filter.qs
        
    paginator = Paginator(art_request_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    art_request_list = paginator.get_page(page_number)

    context={
        'objects':art_request_list,
        'art_request_filter':art_request_filter,
        'segment': segment,
        'table': 'essays/tables/test_request_art.html',
        'search': True,
        'tab':tab
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('essays/tables/test_request_art.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'essays/tables-test_request_art.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_entryelement', raise_exception=True)
def viewEntryElement(request, pk):
    
    entry_element_obj = get_object_or_404(EntryElement, pk=pk)
    segment = 'requests'
    back = '/entry_elements/'

    test_request_obj = None
    if entry_element_obj.has_test_request:
        test_request_obj = entry_element_obj.test_request
        if test_request_obj.closed == True:
            segment = 'closed_test_request'
        elif test_request_obj.touched == False:
            segment = 'requests'
            back = '/test_requests/?touched=False'
        if 'next' in request.GET:
            back =+ request.GET.get('next')
        if 'back' in request.GET:
            back = request.GET.get('back')
        if test_request_obj.deleted and not request.user.has_perm('essays.view_deleted_testrequest'):
            return render(request, 'errors/404.html', status=404)
        
        structure_list = TestStructure.objects.filter(test_request__pk=pk)
        sustrate = None
        if structure_list and test_request_obj.sindex >= 0:
            sustrate = structure_list[test_request_obj.sindex]
        printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
        lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
        cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
        spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
        annexes = Annex.objects.filter(test_request__pk=pk)

    content = 'essays/details/test_request.html'
    
    context = {
        'test_request_obj':test_request_obj,
        'entry_element_obj':entry_element_obj,
        'tab':'main',
        'back': back,
        'content':content,
        'entry_first':True,
        'segment': segment,
    }
    print(context)
    print(entry_element_obj)
    if entry_element_obj.has_test_request:
        context.update({
            'structure_list':structure_list,
            'sustrate':sustrate,
            #'lamination_list':lamination_list,
            'printer_boot':printer_boot,
            'lamination_boot':lamination_boot,
            'cutter_boot':cutter_boot,
            'spec_extra':spec_extra,
            'annexes':annexes,
        })
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_testrequest', raise_exception=True)
def viewTestRequest(request, pk):
    
    test_request_obj = get_object_or_404(TestRequest, pk=pk)
    print("objeto2",test_request_obj)
    segment = 'test_request'
    back = '/test_requests/?touched=True'

    if test_request_obj.closed == True:
        print("Condición: closed == True")
        segment = 'closed_test_request'
    elif test_request_obj.touched == False:
        print("Condición: touched == False")
        segment = 'requests'
        back = '/test_requests/?touched=False'
    if 'next' in request.GET:
        print("Condición: 'next' en request.GET")
        back =+ request.GET.get('next')
    if 'back' in request.GET:
        print("Condición: 'back' en request.GET")
        back = request.GET.get('back')
    if test_request_obj.deleted and not request.user.has_perm('essays.view_deleted_testrequest'):
        print("Condición: deleted y sin permiso")
        return render(request, 'errors/404.html', status=404)
        
    structure_list = TestStructure.objects.filter(test_request__pk=pk)
    print("Estructura de prueba:", structure_list)
    sustrate = None
    if structure_list and test_request_obj.sindex >= 0:
        sustrate = structure_list[test_request_obj.sindex]
    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    content = 'essays/details/test_request.html'
    
    context = {
        'test_request_obj':test_request_obj,
        'structure_list':structure_list,
        'entry_element_obj':test_request_obj.entry_element,
        'sustrate':sustrate,
        #'lamination_list':lamination_list,
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
        'segment': segment,
        'tab':'main',
        'back': back,
        'content':content
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_entryelement', raise_exception=True)
def viewExitElement(request, pk):
    
    exit_element_obj = get_object_or_404(ExitElement, pk=pk)
    segment = 'requests'
    back = '/exit_elements/'

    test_request_obj = exit_element_obj.test_request
    segment = 'closed_test_request'
    if 'next' in request.GET:
        back =+ request.GET.get('next')
    if 'back' in request.GET:
        back = request.GET.get('back')
    if test_request_obj.deleted and not request.user.has_perm('essays.view_deleted_testrequest'):
        return render(request, 'errors/404.html', status=404)
    
    tr = test_request_obj.pk
    structure_list = TestStructure.objects.filter(test_request__pk=tr)
    sustrate = None
    if structure_list and test_request_obj.sindex >= 0:
        sustrate = structure_list[test_request_obj.sindex]
    printer_boot = PrinterBoot.objects.filter(test_request__pk=tr)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=tr)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=tr)
    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=tr)

    content = 'essays/details/test_request.html'
    
    context = {
        'test_request_obj':test_request_obj,
        'entry_element_obj':test_request_obj.entry_element,
        'tab':'exit',
        'back': back,
        'content':content,
        'exit_first':True,
        'segment': segment,
        'structure_list':structure_list,
        'sustrate':sustrate,
        #'lamination_list':lamination_list,
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_printerboot', raise_exception=True)
def viewPrinterBoot(request, pk, ck):
    
    test_request_obj = get_object_or_404(TestRequest, pk=pk)
    segment = 'test_request'
    back = '/test_requests/?touched=True'
    if test_request_obj.touched == False:
        segment = 'requests'
        back = '/test_requests/?touched=False'
    if 'next' in request.GET:
        back =+ request.GET.get('next')
    printer_boot_obj = get_object_or_404(PrinterBoot, pk=ck)
    sustrate = None
    if test_request_obj.sindex >= 0:
        sustrate = TestStructure.objects.filter(test_request__pk = pk)[test_request_obj.sindex]
    test_file = TestFile.objects.filter(boot_p=ck)
    result_cols_list = []
    bobbin_id_list = []
    
    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    for test in test_file:
        essays = TestFileEssay.objects.filter(test_file=test)
        if essays:
            results = TestFileEssayResult.objects.filter(essay=essays[0])
            result_cols_list.append(len(results))
            bobbin_id_list.append(results)
        else:
            result_cols_list.append(0)
            bobbin_id_list.append(0)
    
    objects = zip(test_file, result_cols_list, bobbin_id_list)

    content ='essays/details/machine_boot.html'
    context = {
        'test_request_obj':test_request_obj,
        'printer_boot_obj':printer_boot_obj,
        'tab':'printer_boot',
        'sustrate':sustrate,
        'objects':objects,
        'test_file':test_file,
        'segment':segment,
        'back': back,
        'content':content,
        'tab_p':printer_boot_obj.id, #type:ignore
        #render tabs--------------------
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_laminatorboot', raise_exception=True)
def viewLaminatorBoot(request, pk, ck):
    
    test_request_obj = get_object_or_404(TestRequest, pk=pk)
    segment = 'test_request'
    back = '/test_requests/?touched=True'
    if test_request_obj.touched == False:
        segment = 'requests'
        back = '/test_requests/?touched=False'
    if 'next' in request.GET:
        back =+ request.GET.get('next')
    lamination_boot_obj = get_object_or_404(LaminatorBoot, pk=ck)
    lamination_essay = LaminationEssay.objects.filter(laminator_boot=lamination_boot_obj).order_by('essay__priority')
    test_file = TestFile.objects.filter(boot_l=ck)
    result_cols_list = []
    bobbin_id_list = []
    
    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    for test in test_file:
        essays = TestFileEssay.objects.filter(test_file=test)
        if essays:
            results = TestFileEssayResult.objects.filter(essay=essays[0])
            result_cols_list.append(len(results))
            bobbin_id_list.append(results)
        else:
            result_cols_list.append(0)
            bobbin_id_list.append(0)
    
    objects = zip(test_file, result_cols_list, bobbin_id_list)

    content ='essays/details/machine_boot.html'

    context = {
        'test_request_obj':test_request_obj,
        'lamination_boot_obj':lamination_boot_obj,
        'lamination_essay':lamination_essay,
        'tab':'laminator_boot',
        'objects':objects,
        'test_file':test_file,
        'segment':segment,
        'back': back,
        'content':content,
        'tab_l':lamination_boot_obj.id, #type:ignore
        #render tabs--------------------
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_cutterboot', raise_exception=True)
def viewCutterBoot(request, pk, ck):
    
    test_request_obj = get_object_or_404(TestRequest, pk=pk)
    segment = 'test_request'
    back = '/test_requests/?touched=True'
    if test_request_obj.touched == False:
        segment = 'requests'
        back = '/test_requests/?touched=False'
    if 'next' in request.GET:
        back =+ request.GET.get('next')
    cutter_boot_obj = get_object_or_404(CutterBoot, pk=ck)
    
    structure_list = TestStructure.objects.filter(test_request__pk=pk)
    tr_weight = 0
    for st in structure_list:
        tr_weight = tr_weight + st.weight #type:ignore

    #render the tabs------------------------------------------------------------------
    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    content ='essays/details/cutter_boot.html'

    context = {
        'test_request_obj':test_request_obj,
        'cutter_boot_obj':cutter_boot_obj,
        'tr_weight':tr_weight,
        'segment':segment,
        'back': back,
        'content':content,
        'tab_c':cutter_boot_obj.id, #type:ignore
        #render tabs--------------------
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_technicalspecs', raise_exception=True)
def viewTechSpecs(request, pk):
    
    test_request_obj = get_object_or_404(TestRequest, pk=pk)
    if test_request_obj.deleted and not request.user.has_perm('essay.view_deleted_testrequest'):
        return render(request, 'errors/404.html', status=404)
    segment = 'test_request'
    back = '/test_requests/?touched=True'
    if test_request_obj.touched == False:
        segment = 'requests'
        back = '/test_requests/?touched=False'
    if 'next' in request.GET:
        back =+ request.GET.get('next')
    structure_list = TestStructure.objects.filter(test_request__pk=pk)

    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)

    latest_lam = None
    latest_report = None
    latest_cutter = None

    if lamination_boot:
        latest_lam = lamination_boot.latest('id')
        reports = TestFile.objects.filter(boot_l__id=latest_lam.pk)
        latest_report = reports.last()
    elif printer_boot:
        latest_lam = printer_boot.latest('id')
        reports = TestFile.objects.filter(boot_p__id=latest_lam.pk)
        latest_report = reports.last()

    if cutter_boot:
        latest_cutter = cutter_boot.latest('id')

    all_delal = TestFileEssay.objects.filter(test_file__boot_l__test_request=test_request_obj).filter(essay__method="011").order_by('test_file__boot_l__step')

    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    content = 'essays/details/tech_specs.html'
    
    context = {
        'test_request_obj':test_request_obj,
        'structure_list':structure_list,
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'latest_lam':latest_lam,
        'latest_report':latest_report,
        'all_delal':all_delal,
        'cutter_boot':cutter_boot,
        'latest_cutter':latest_cutter,
        'spec_extra':spec_extra,
        'tab_ts':True,
        'annexes':annexes,
        'segment':segment,
        'tab':'tech_specs',
        'back': back,
        'content':content
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

#Art Request Crud------------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/login/')    
@permission_required('essays.add_artrequest', raise_exception=True)#type:ignore
@transaction.atomic
def addArtRequest (request, entry_element_id=None):
    form = ArtRequestForm(request.POST or None)
    sformset = ArtStructureFormset(request.POST or None, prefix='structures')

    entry_element = get_object_or_404(ArtEntryElement, pk=entry_element_id) if entry_element_id else None
    
    context = {'form': form, 'sformset': sformset, 'segment':'requests_art', 'entry_element':entry_element, 'back': True}
    last_tr = ArtRequest.objects.exclude(deleted=True).order_by('-number')
    
    last = last_tr[0].number if last_tr else "03-000000"

    if request.method == 'POST':
        if form.is_valid() and sformset.is_valid():
            art_request = form.save(commit=False)
            #validation
            if art_request.art_number:
                art_request.art_number = art_request.art_number.upper()

            if not art_request.number:
                art_request.number = set_tr_number(str(last)) 

            if not request.user.has_perm('essays.sign_artrequest'):
                art_request.reviewer = None
            if entry_element:
                art_request.entry_element = entry_element

            art_request.id = get_id(ArtRequest)
            art_request.date = timezone.now()

            art_request.save()

            sform = sformset.save(commit=False)
            for structure in sform:
                structure.test_request = art_request
                if structure.code is not None:
                    structure.code = structure.code.upper()
                structure.save()

            action = bool(request.POST.get('save_and_view'))
            
            if action == True:
                return redirect('view_test_request_art', art_request.id)
            
            return redirect('/test_requests_art/?touched=False')
        else:
            print(form.errors)
    return render(request, 'essays/form-art-request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.add_artrequest', raise_exception=True)#type:ignore
@transaction.atomic
def cloneArtRequest(request, pk):
    with CaptureQueriesContext(connection) as context:

        test_request = ArtRequest.objects.get(id=pk)
        test = ArtStructure.objects.filter(test_request__pk=pk)

        test_request.id = get_id(ArtRequest) #type:ignore
        test_request.entry_element = None
        test_request.deleted = False
        test_request.deleted_by = None
        test_request.deleted_time = None
        test_request.deleted_reason = None
        test_request.archived = False
        test_request.archived_time = None
        test_request.closed = False
        test_request.closed_time = None
        test_request.touched = False
        test_request.number = None
        test_request.production_order = ''
        test_request.reviewer = None

        test_request.save()

        test_request_id = test_request

        new_tests = []
        for ts in test:
            ts.id = None #type:ignore
            ts.test_request = test_request_id #type:ignore
            new_tests.append(ts)

        TestStructure.objects.bulk_create(new_tests)

        #print(f"The function made {len(context)} queries.")

    request.session['header'] = 'review'
    return redirect('test_request_art')

@login_required(login_url='/login/')
@permission_required('essays.view_testrequest', raise_exception=True)
def viewArtRequest(request, pk):
    
    test_request_obj = get_object_or_404(ArtRequest, pk=pk)
    segment = 'test_request_art'
    back = '/test_requests_art/?touched=True'
    print("objeto",test_request_obj)
    if test_request_obj.closed == True:
        print("Condición: closed == True")
        segment = 'closed_test_request_art'
    elif test_request_obj.touched == False:
        print("Condición: touched == False")
        segment = 'requests_art'
        back = '/test_requests_art/?touched=False'
    if 'next' in request.GET:
        print("Condición: 'next' en request.GET")
        back =+ request.GET.get('next')
    if 'back' in request.GET:
        print("Condición: 'back' en request.GET")
        back = request.GET.get('back')
    if test_request_obj.deleted and not request.user.has_perm('essays.view_deleted_artrequest'):
        print("Condición: deleted y sin permiso")
        return render(request, 'errors/404.html', status=404)
    
    structure_list = ArtStructure.objects.filter(test_request__pk=pk)
    print("estructura",structure_list)
    sustrate = None
    if structure_list and test_request_obj.sindex >= 0:
        sustrate = structure_list[test_request_obj.sindex]
    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
    spec_extra = ArtTechnicalSpecs.objects.filter(art_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    content = 'essays/details/test_request_art.html'
    
    context = {
        'test_request_obj':test_request_obj,
        'structure_list':structure_list,
        'entry_element_obj':test_request_obj.entry_element,
        'sustrate':sustrate,
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
        'segment': segment,
        'tab':'main',
        'back': back,
        'content':content
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request_art.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_testrequest', raise_exception=True)#type:ignore
@transaction.atomic
def editArtRequest(request, pk):
    
    obj = get_object_or_404(ArtRequest, pk=pk)
    
    try:
        entry_element = obj.entry_element
    except:
        entry_element = None

    segment = 'test_request_art'
    if obj.deleted or \
    (obj.reviewer and not request.user.has_perm('essays.sign_artrequest')):
        return render(request, 'errors/403.html', status=403)
    if obj.touched == False:
        segment = 'requests_art'
    #elif not request.user.is_superuser and obj.touched:
    #    return render(request, 'errors/403.html', status=403)
    form = ArtRequestForm(request.POST or None, instance=obj)
    sformset = ArtStructureFormset(request.POST or None, instance = obj, prefix='structures')

    context = {'form': form,'sformset': sformset, 'segment':segment, 'entry_element':entry_element, 'back': True}
    if request.method == 'POST':
        if form.is_valid() and sformset.is_valid():
            test_request = form.save(commit=False)
            #validation
            if test_request.art_number:
                test_request.art_number = test_request.art_number.upper()
            
            #add if update date true from the request
            if request.POST.get('update_date'):
                test_request.date = timezone.now()
            
            if not test_request.number:
                last = ArtRequest.objects.exclude(deleted=True).exclude(pk=pk).order_by('-number')[0]
                test_request.number = set_tr_number(last.number) #type:ignore

            if not request.user.has_perm('essays.sign_artrequest'):
                test_request.reviewer = obj.reviewer or None

            test_request.save(force_update=True)

            sform = sformset.save(commit=False)

            for rms in sformset.deleted_objects:
                rms.delete()

            for structure in sform:
                if not structure.id:
                    structure.test_request = test_request
                if structure.code is not None:
                    structure.code = structure.code.upper()
                structure.save() 

            action = bool(request.POST.get('save_and_view'))
            
            if action == True:
                print("Redirigiendo a view_test_request_art")
                return redirect('view_test_request_art', test_request.id)
            
            if 'next' in request.GET:
                print("Redirigiendo a next")
                return redirect(request.GET.get('next'))
            
            print("Redirigiendo a /test_requests_art/?touched=False")
            return redirect('/test_requests_art/?touched=False')
        else:
            for err in form.errors:
                print(err)
    return render(request, 'essays/form-art-request.html', context)


@login_required(login_url='/login/')
@permission_required('essays.change_testrequest', raise_exception=True)#type:ignore
@transaction.atomic
def editTestRequest (request, pk):
    
    obj = get_object_or_404(TestRequest, pk=pk)
    
    try:
        entry_element = obj.entry_element
    except:
        entry_element = None

    segment = 'test_request'
    if obj.deleted or \
    (obj.reviewer and not request.user.has_perm('essays.sign_testrequest')):
        return render(request, 'errors/403.html', status=403)
    if obj.touched == False:
        segment = 'requests'
    #elif not request.user.is_superuser and obj.touched:
    #    return render(request, 'errors/403.html', status=403)
    form = TestRequestForm(request.POST or None, instance=obj)
    sformset = TestStructureFormset(request.POST or None, prefix='structures')

    context = {'form': form,'sformset': sformset, 'segment':segment, 'entry_element':entry_element, 'back': True}
    if request.method == 'POST':
        if form.is_valid() and sformset.is_valid():
            test_request = form.save(commit=False)
            #validation
            if test_request.art_number:
                test_request.art_number = test_request.art_number.upper()
            
            #add if update date true from the request
            if request.POST.get('update_date'):
                test_request.date = timezone.now()
            
            if not test_request.number:
                last = TestRequest.objects.exclude(deleted=True).exclude(pk=pk).order_by('-number')[0]
                test_request.number = set_tr_number(last.number) #type:ignore

            if not request.user.has_perm('essays.sign_testrequest'):
                test_request.reviewer = obj.reviewer or None

            test_request.save(force_update=True)

            sform = sformset.save(commit=False)

            for rms in sformset.deleted_objects:
                rms.delete()

            for structure in sform:
                if not structure.id:
                    structure.test_request = test_request
                if structure.code is not None:
                    structure.code = structure.code.upper()
                structure.save() 

            action = bool(request.POST.get('save_and_view'))
            
            if action == True:
                return redirect('view_test_request', test_request.id)
            
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            
            return redirect('/test_requests/?touched=False')
        else:
            for err in form.errors:
                return redirect('/test_requests/?touched=False')
    else:
        for err in form.errors:
            print(err)
    return render(request, 'essays/form-test_request.html', context)
 
#Test Request Crud------------------------------------------------------------------------------------------------------------------------>
def set_tr_number(val: str) -> str:
    lead, string = val.split("-")
    new_string = str(int(string) + 1).zfill(len(string))
    return f"{lead}-{new_string}"

@login_required(login_url='/login/')
@permission_required('essays.add_testrequest', raise_exception=True)#type:ignore
@transaction.atomic
def cloneTestRequest(request, pk):
    with CaptureQueriesContext(connection) as context:

        test_request = TestRequest.objects.get(id=pk)
        test = TestStructure.objects.filter(test_request__pk=pk)

        test_request.id = get_id(TestRequest) #type:ignore
        test_request.entry_element = None
        test_request.deleted = False
        test_request.deleted_by = None
        test_request.deleted_time = None
        test_request.deleted_reason = None
        test_request.archived = False
        test_request.archived_time = None
        test_request.closed = False
        test_request.closed_time = None
        test_request.touched = False
        test_request.number = None
        test_request.production_order = ''
        test_request.reviewer = None

        test_request.save()

        test_request_id = test_request

        new_tests = []
        for ts in test:
            ts.id = None #type:ignore
            ts.test_request = test_request_id #type:ignore
            new_tests.append(ts)

        TestStructure.objects.bulk_create(new_tests)

        #print(f"The function made {len(context)} queries.")

    request.session['header'] = 'review'
    return redirect('test_request')

#------------------------------Crear una solicitud de ensayo------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
@permission_required('essays.add_testrequest', raise_exception=True)#type:ignore
@transaction.atomic
def addTestRequest (request, entry_element_id=None):
    
    form = TestRequestForm(request.POST or None)
    sformset = TestStructureFormset(request.POST or None, prefix='structures')

    entry_element = get_object_or_404(EntryElement, pk=entry_element_id) if entry_element_id else None
    
    context = {'form': form, 'sformset': sformset, 'segment':'requests', 'entry_element':entry_element, 'back': True}
    last_tr = TestRequest.objects.exclude(deleted=True).order_by('-number')
    
    last = last_tr[0].number if last_tr else "03-000000"


    if request.method == 'POST':
        if form.is_valid() and sformset.is_valid():
            test_request = form.save(commit=False)
            #validation
            if test_request.art_number:
                test_request.art_number = test_request.art_number.upper()

            if not test_request.number:
                test_request.number = set_tr_number(str(last)) 

            if not request.user.has_perm('essays.sign_testrequest'):
                test_request.reviewer = None
            if entry_element:
                test_request.entry_element = entry_element

            test_request.id = get_id(TestRequest)
            test_request.date = timezone.now()

            test_request.save()

            sform = sformset.save(commit=False)
            for structure in sform:
                structure.test_request = test_request
                if structure.code is not None:
                    structure.code = structure.code.upper()
                structure.save()

            action = bool(request.POST.get('save_and_view'))
            
            if action == True:
                return redirect('view_test_request', test_request.id)
            
            return redirect('/test_requests/?touched=False')
        else:
            print(form.errors)
    return render(request, 'essays/form-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_testrequest', raise_exception=True)#type:ignore
@transaction.atomic
def editTestRequest (request, pk):
    
    obj = get_object_or_404(TestRequest, pk=pk)
    
    try:
        entry_element = obj.entry_element
    except:
        entry_element = None

    segment = 'test_request'
    if obj.deleted or \
    (obj.reviewer and not request.user.has_perm('essays.sign_testrequest')):
        return render(request, 'errors/403.html', status=403)
    if obj.touched == False:
        segment = 'requests'
    #elif not request.user.is_superuser and obj.touched:
    #    return render(request, 'errors/403.html', status=403)
    form = TestRequestForm(request.POST or None, instance=obj)
    sformset = TestStructureFormset(request.POST or None, prefix='structures')

    context = {'form': form,'sformset': sformset, 'segment':segment, 'entry_element':entry_element, 'back': True}
    if request.method == 'POST':
        if form.is_valid() and sformset.is_valid():
            test_request = form.save(commit=False)
            #validation
            if test_request.art_number:
                test_request.art_number = test_request.art_number.upper()
            
            #add if update date true from the request
            if request.POST.get('update_date'):
                test_request.date = timezone.now()
            
            if not test_request.number:
                last = TestRequest.objects.exclude(deleted=True).exclude(pk=pk).order_by('-number')[0]
                test_request.number = set_tr_number(last.number) #type:ignore

            if not request.user.has_perm('essays.sign_testrequest'):
                test_request.reviewer = obj.reviewer or None

            test_request.save(force_update=True)

            sform = sformset.save(commit=False)

            for rms in sformset.deleted_objects:
                rms.delete()

            for structure in sform:
                if not structure.id:
                    structure.test_request = test_request
                if structure.code is not None:
                    structure.code = structure.code.upper()
                structure.save() 

            action = bool(request.POST.get('save_and_view'))
            
            if action == True:
                return redirect('view_test_request', test_request.id)
            
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            
            return redirect('/test_requests/?touched=False')
        else:
            for err in form.errors:
                return redirect('/test_requests/?touched=False')
    else:
        for err in form.errors:
            print(err)
    return render(request, 'essays/form-test_request.html', context)

def deleteTestRequest(request, pk):
    test_request = get_object_or_404(TestRequest, pk=pk)
     
    if test_request.deleted or \
    (test_request.reviewer and not request.user.has_perm('essays.sign_testrequest')):
        return render(request, 'errors/403.html', status=403)
    if not request.user.is_superuser and test_request.touched:
        return render(request, 'errors/404.html', status=404)
        
    test_request.deleted = True
    test_request.deleted_by = request.user.username
    test_request.deleted_reason = request.POST.get('deleted_reason')
    test_request.deleted_time = timezone.now()

    test_request.save()

    #something to redirect to unsigned test request
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
        
    return redirect('/test_requests/?touched=False') 
    
@login_required(login_url='/login/')
@permission_required('essays.delete_true_testrequest', raise_exception=True)#type:ignore
def deleteTrueTestRequest(request, pk):
    test_request = get_object_or_404(TestRequest, pk=pk)
    if not test_request.deleted:
        return render(request, 'errors/400.html', status=400)
    if request.method == 'POST':
        test_request.delete()
    return redirect('/test_requests/?touched=False')
    
@login_required(login_url='/login/')
@permission_required('essays.restore_testrequest', raise_exception=True)
def restoreTestRequest(request, pk):

    obj = get_object_or_404(TestRequest, pk=pk)

    obj.deleted = False
    obj.deleted_reason = None
    obj.deleted_by = None
    obj.deleted_time = None
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests/?touched=False')

@login_required(login_url='/login/')
@permission_required('essays.close_testrequest', raise_exception=True)
def closeTestRequest(request, pk):

    obj = get_object_or_404(TestRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.closed = True
    obj.closed_time = timezone.now()
    
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests/?touched=closed')

@login_required(login_url='/login/')
@permission_required('essays.archive_testrequest', raise_exception=True)
def archiveTestRequest(request, pk):

    obj = get_object_or_404(TestRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.archived = True
    obj.archived_time = timezone.now()
    
    obj.save()
    
    request.session['header'] = 'archived'

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests/?touched=false')

@login_required(login_url='/login/')
@permission_required('essays.unarchive_testrequest', raise_exception=True)
def unarchiveTestRequest(request, pk):

    obj = get_object_or_404(TestRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.archived = False
    obj.archived_time = None
    
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests/?touched=false')

@login_required(login_url='/login/')
@permission_required('essays.open_testrequest', raise_exception=True)
def openTestRequest(request, pk):

    obj = get_object_or_404(TestRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.closed = False
    obj.closed_time = None
    
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests/?touched=closed')

@login_required(login_url='/login/')
@permission_required('essays.delete_artrequest', raise_exception=True)#type:ignore
def deleteTestRequestArt(request, pk):
    art_request = get_object_or_404(ArtRequest, pk=pk)
     
    if art_request.deleted or \
    (art_request.reviewer and not request.user.has_perm('essays.sign_artrequest')):
        return render(request, 'errors/403.html', status=403)
    if not request.user.is_superuser and art_request.touched:
        return render(request, 'errors/404.html', status=404)
        
    art_request.deleted = True
    art_request.deleted_by = request.user.username
    art_request.deleted_reason = request.POST.get('deleted_reason')
    art_request.deleted_time = timezone.now()

    art_request.save()

    #something to redirect to unsigned test request
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
        
    return redirect('/test_requests_art/?touched=False')
    
@login_required(login_url='/login/')
@permission_required('essays.delete_true_testrequest', raise_exception=True)#type:ignore
def deleteTrueTestRequestArt(request, pk):
    test_request = get_object_or_404(ArtRequest, pk=pk)
    if not test_request.deleted:
        return render(request, 'errors/400.html', status=400)
    if request.method == 'POST':
        test_request.delete()
    return redirect('/test_requests_art/?touched=False')
    
@login_required(login_url='/login/')
@permission_required('essays.restore_artrequest', raise_exception=True)
def restoreTestRequestArt(request, pk):

    obj = get_object_or_404(ArtRequest, pk=pk)

    obj.deleted = False
    obj.deleted_reason = None
    obj.deleted_by = None
    obj.deleted_time = None
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests_art/?touched=False')

@login_required(login_url='/login/')
@permission_required('essays.close_testrequest', raise_exception=True)
def closeTestRequestArt(request, pk):

    obj = get_object_or_404(TestRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.closed = True
    obj.closed_time = timezone.now()
    
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests_art/?touched=closed')

@login_required(login_url='/login/')
@permission_required('essays.archive_artrequest', raise_exception=True)
def archiveTestRequestArt(request, pk):

    obj = get_object_or_404(ArtRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.archived = True
    obj.archived_time = timezone.now()
    
    obj.save()
    
    request.session['header'] = 'archived'

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests_art/?touched=false')

@login_required(login_url='/login/')
@permission_required('essays.unarchive_artrequest', raise_exception=True)
def unarchiveTestRequestArt(request, pk):

    obj = get_object_or_404(ArtRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.archived = False
    obj.archived_time = None
    
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests_art/?touched=false')

@login_required(login_url='/login/')
@permission_required('essays.open_artrequest', raise_exception=True)
def openTestRequestArt(request, pk):

    obj = get_object_or_404(ArtRequest, pk=pk)

    if obj.deleted == True:
        return render(request, 'errors/403.html', status=403)
    
    obj.closed = False
    obj.closed_time = None
    
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('/test_requests_art/?touched=closed')

#Printer Boot----------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('essays.add_printerboot', raise_exception=True)#type:ignore
def addPrinterBootTR (request, tr):
    
    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the parent to render
    
    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    form = PrinterBootForm(request.POST or None)

    sustrate = None
    if test_request_obj.sindex >= 0:
        sustrate = TestStructure.objects.filter(test_request__pk = tr)[test_request_obj.sindex]
    context = {'form': form, 'test_request_obj':test_request_obj, 'sustrate':sustrate, 'segment':'test_request', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            printer_boot = form.save(commit=False)
            #validation
            for i in range(1, 11):
                attr = f'sta_{i:02d}'
                value = getattr(printer_boot, attr, None)
                if value is not None:
                    setattr(printer_boot, attr, value.upper())

            printer_boot.test_request = test_request_obj

            printer_boot.r_average = average(printer_boot.r_left, printer_boot.r_right, printer_boot.r_center)            

            printer_boot.save()

            test_request_obj.touched = True
            test_request_obj.production_order = request.POST.get('production_order')
            test_request_obj.save()

            return redirect(f'/test_requests/{test_request_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-printer_boot.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_printerboot', raise_exception=True)#type:ignore
def editPrinterBootTR (request, tr, ck):
    
    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the parent to render

    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    printer_boot_obj = get_object_or_404(PrinterBoot, pk=ck)

    form = PrinterBootForm(request.POST or None, instance=printer_boot_obj)
    sustrate = None
    if test_request_obj.sindex >= 0:
        sustrate = TestStructure.objects.filter(test_request__pk = tr)[test_request_obj.sindex]

    context = {'form': form, 'test_request_obj':test_request_obj, 'printer_boot_obj':printer_boot_obj, 'sustrate':sustrate, 'segment':'test_request', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            printer_boot = form.save(commit=False)
            #validation
            for i in range(1, 11):
                attr = f'sta_{i:02d}'
                value = getattr(printer_boot, attr, None)
                if value is not None:
                    setattr(printer_boot, attr, value.upper())
            printer_boot.test_request = test_request_obj
            
            printer_boot.r_average = average(printer_boot.r_left, printer_boot.r_right, printer_boot.r_center)

            printer_boot.save()

            test_request_obj.touched = True
            test_request_obj.production_order = request.POST.get('production_order')
            test_request_obj.save()
                
            return redirect(f'/test_requests/{test_request_obj.id}/printer/{printer_boot_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-printer_boot.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_printerboot', raise_exception=True)#type:ignore
def deletePrinterBootTR (request, tr, ck):

    if TestRequest.objects.get(pk = tr).signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    printr_boot = get_object_or_404(PrinterBoot, pk=ck)
    if request.method == 'POST':
        printr_boot.delete()
    return redirect('view_test_request', tr)

#Laminator Boot----------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('essays.add_laminatorboot', raise_exception=True)#type:ignore
@transaction.atomic
def addLaminatorBootTR (request, tr):
    
    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the parent to render

    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    form = LaminatorBootForm(request.POST or None)
    formset_essay = LaminationEssayFormset(request.POST or None, prefix='essays')

    context = {'form': form, 'formset_essay': formset_essay, 'test_request_obj':test_request_obj, 'segment':'test_request', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid() and formset_essay.is_valid():

            laminator_boot = form.save(commit=False)
            laminator_boot.test_request = test_request_obj
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
            
            test_request_obj.touched = True
            test_request_obj.production_order = request.POST.get('production_order')
            test_request_obj.save()    

            return redirect(f'/test_requests/{test_request_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-laminator_boot.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_laminatorboot', raise_exception=True)#type:ignore
@transaction.atomic
def editLaminatorBootTR (request, tr, ck):
    
    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the parent to render

    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    lamination_obj = get_object_or_404(LaminatorBoot, pk=ck)#Get the parent to render

    form = LaminatorBootForm(request.POST or None, instance=lamination_obj)
    formset_essay = LaminationEssayFormset(request.POST or None, prefix='essays', instance=lamination_obj)

    context = {'form': form, 'formset_essay': formset_essay, 'test_request_obj':test_request_obj, 'lamination_obj':lamination_obj, 'segment':'test_request', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid() and formset_essay.is_valid():
            laminator_boot = form.save(commit=False)
            #validation            
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
                
            test_request_obj.touched = True
            test_request_obj.production_order = request.POST.get('production_order')
            test_request_obj.save()
            
            return redirect(f'/test_requests/{test_request_obj.id}/laminator/{lamination_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-laminator_boot.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_laminatorboot', raise_exception=True)#type:ignore
def deleteLaminatorBootTR (request, tr, ck):

    if TestRequest.objects.get(pk = tr).signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    laminator_boot = get_object_or_404(LaminatorBoot, pk=ck)
    if request.method == 'POST':
        laminator_boot.delete()
    return redirect('view_test_request', tr)

#Export Boot-------------------------------------------------------------------------------->    
@login_required(login_url='/login/')
@permission_required('essays.export_boot', raise_exception=True)#type:ignore
@transaction.atomic
def ExportBoot(request, pk, machine, ck):
    
    if request.method == 'POST':
        parent = get_object_or_404(TestRequest, pk=pk)
        provider = None
        if parent.sindex >=0:
            test_structure = TestStructure.objects.filter(test_request__id=pk)[parent.sindex]
            provider = test_structure.provider

        destiny_type, destiny_id = request.POST.get('destiny_document').split('-')
        if destiny_type == 'OP':
            destiny_document = get_object_or_404(Order, pk=destiny_id)
            address = 'production'
        elif destiny_type == 'PR':
            destiny_document = get_object_or_404(TestRequest, pk=destiny_id)
            address = 'test_requests'

        if destiny_type == 'OP':
            model_mapping = {
                'PrinterBoot': ProductionPrinterBoot,
                'LaminatorBoot': ProductionLaminatorBoot,
                'LaminationEssay':ProductionLaminationEssay,
                'TestFile': ProductionTestFile,
                'TestFileEssay': ProductionTestFileEssay,
                'TestFileEssayResult': ProductionTestFileEssayResult,
                'Bobbin': ProductionBobbin,
            }

        elif destiny_type == 'PR':
            model_mapping = {
                'PrinterBoot': PrinterBoot,
                'LaminatorBoot': LaminatorBoot,
                'LaminationEssay':LaminationEssay,
                'TestFile': TestFile,
                'TestFileEssay': TestFileEssay,
                'TestFileEssayResult': TestFileEssayResult,
                'Bobbin': Bobbin,
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
        del data['test_request_id']

        if not data['origin']:
            data['origin'] = f'PR-{parent.production_order}'

        if destiny_type == 'OP':
            data['production_order_id'] = destiny_id

            if machine == 'printer':
                data['s_index'] = parent.sindex
                data['provider'] = provider
                data['sustrate_width'] = parent.sustrate_width

        elif destiny_type == 'PR':
            data['test_request_id'] = destiny_id

        if machine == 'printer':
            boot = model_mapping['PrinterBoot'](**data)
        elif machine == 'laminator':
            boot = model_mapping['LaminatorBoot'](**data)

        boot.save()
        
        for related_object in machine_types[machine].objects.get(id=og_boot_id)._meta.related_objects:
            if related_object.one_to_many and related_object.field.name not in ['production_operator', 'quality_analist']:
                for obj in getattr(machine_types[machine].objects.get(id=og_boot_id), related_object.get_accessor_name()).all():
                    ####warning when cloning laminatror boot, the related laminator eassays get in the way and intefere with the testFiles
                    obj_data = deepcopy(obj)
                    data_2 = obj_data.__dict__
                    del data_2['_state']
                    del data_2['_django_version']
                    del data_2['id']
                    data_2[f'{related_object.field.name}_id'] = boot.id
                    
                    #catching laminator essay objects  
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

        return redirect(f'/{address}/{destiny_document.id}/{machine}/{boot.id}')#type:ignore

    return HttpResponseBadRequest(request)



#Unified Report CRUD------------------------------------------------------------------------>    
@login_required(login_url='/login/')
@permission_required('essays.add_testfile', raise_exception=True)#type:ignore
@transaction.atomic
def Report(request, tr, ck, boot_type):

    test_request_obj = get_object_or_404(TestRequest, pk=tr)  # Get the parent to render

    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    if boot_type == 'laminator':
        boot_obj = get_object_or_404(LaminatorBoot, pk=ck)  # Get the parent to render
    elif boot_type == 'printer':
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
        'test_request_obj':test_request_obj,
        'boot_obj':boot_obj,
        'segment':'test_request',
        'back': True
    }

    if request.method == 'POST':
        
        if form.is_valid() and formset_essay.is_valid() and formset_essay_result.is_valid():
            test_file = form.save(commit=False)
            # validation
            if boot_type == 'laminator':
                test_file.boot_l = boot_obj
            elif boot_type == 'printer':
                test_file.boot_p = boot_obj

            if not request.user.has_perm('essays.supv_sign_testfile'):
                test_file.supervisor = None
            if not request.user.has_perm('essays.boss_sign_testfile'):
                test_file.boss = None
            if not request.user.has_perm('home.sign_plan'):
                test_file.idat = None
            test_file.save()
            bobbin = Bobbin.objects.create(test_file = test_file, turn=test_file.turn, date=test_file.date, quality_analist=test_file.quality_analist, production_operator=test_file.production_operator)

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
            
            test_request_obj.touched = True
            test_request_obj.save()

            return redirect(f'/test_requests/{test_request_obj.id}/{boot_type}/{boot_obj.id}')  # type:ignore
        else:
            print(form.errors)
            print(formset_essay.errors)
            print(formset_essay_result.errors)
    return render(request, 'essays/form-test_file.html', context)

@login_required(login_url='/login/')
@permission_required('essays.view_testfile', raise_exception=True)#type:ignore
def editReport(request, tr, ck, rp, boot_type):

    test_request_obj = get_object_or_404(TestRequest, pk=tr)  # Get the parent to render
    
    ug = request.user.groups

    if test_request_obj.signed_techspecs and not (ug.filter(name = 'ASCA-Staff').exists() or ug.filter(name = 'IDAT-A').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    if boot_type == 'laminator':
        boot_obj = get_object_or_404(LaminatorBoot, pk=ck)  # Get the parent to render
    elif boot_type == 'printer':
        boot_obj = get_object_or_404(PrinterBoot, pk=ck)  # Get the parent to render
    else:
        raise Http404("Invalid boot type")

    test_file_obj = get_object_or_404(TestFile, pk=rp)
    form = TestFileForm(request.POST or None, instance=test_file_obj, user=request.user)

    context = {
        'form': form, 
        'test_request_obj': test_request_obj,
        'boot_obj': boot_obj,
        'segment': 'test_request',
        'back': True
    }

    if request.method == 'POST':
        if form.is_valid():
            test_file = form.save(commit=False)
            if request.user.has_perm('home.sign_plan'):
                test_file.turn = test_file_obj.turn
                test_file.date = test_file_obj.date
                test_file.quality_analist = test_file_obj.quality_analist
                test_file.production_operator = test_file_obj.production_operator
                test_file.supervisor = test_file_obj.supervisor
                test_file.boss = test_file_obj.boss
                test_file.save()

                test_request_obj.touched = True
                test_request_obj.save()

                return redirect(f'/test_requests/{test_request_obj.id}/{boot_type}/{boot_obj.id}')  # type:ignore
            # validation
            if not request.user.has_perm('essays.supv_sign_testfile'):
                test_file.supervisor = test_file_obj.supervisor or None
            if not request.user.has_perm('essays.boss_sign_testfile'):
                test_file.boss = test_file_obj.boss or None
            if not request.user.has_perm('home.sign_plan'):
                test_file.idat = test_file_obj.idat or None
            test_file.save()

            test_request_obj.touched = True
            test_request_obj.save()

            return redirect(f'/test_requests/{test_request_obj.id}/{boot_type}/{boot_obj.id}')  # type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-test_file.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_testfile', raise_exception=True)#type:ignore
def deleteReport(request, tr, ck, rp, boot_type):

    if TestRequest.objects.get(pk = tr).signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    report = get_object_or_404(TestFile, pk=rp)
    if request.method == 'POST':
        report.delete()
    return redirect(f'/test_requests/{tr}/{boot_type}/{ck}')

#Test Files------------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('essays.add_testfileessayresult', raise_exception=True)#type:ignore
@transaction.atomic
def addResult (request, tr, machine, ck, tf):

    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the grandparent to render

    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

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

            test_request_obj.touched = True
            test_request_obj.save()

           
            return redirect(f'/test_requests/{tr}/{machine}/{ck}')
        else:
            print(formset.errors)
    else:
        formset = FromsetResults(queryset=TestFileEssayResult.objects.none(), prefix='results')
    context = {
        'formset': formset,
        'essays': essays,
        'curr_bobbin': curr_bobbin,
        'test_request_obj':test_request_obj,
        'analyst':analyst,
        'operator':operator,
        'segment':'test_request',
        'back': True
    }

    return render(request, 'essays/form-result_add.html', context)

@login_required(login_url='/login/')
@permission_required('essays.add_testfileessay', raise_exception=True)#type:ignore
@transaction.atomic
def addTestFileEssay (request, pk, tr, site, ck):    
    
    test_file = TestFile.objects.get(pk=pk)

    if test_file.boot.test_request.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser): #type:ignore
        return render(request, 'errors/403.html', status=403)

    results = []
    
    essays = TestFileEssay.objects.filter(test_file=test_file)
    if essays:
        results = TestFileEssayResult.objects.filter(essay=essays[0])
    else:
        results.append('na')

    form = TestFileEssayForm(request.POST or None)
    formset = TestFileEssayResultFormset(request.POST or None, queryset=TestFileEssayResult.objects.none(), prefix='results')

    context = {'form': form, 'formset': formset, 'results': results, 'result_total': len(results), 'segment':'test_request', 'back': True}

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

            if site == 'p':
                return redirect(f'/test_requests/{tr}/printer/{ck}')
            else:
                return redirect(f'/test_requests/{tr}/laminator/{ck}')
        else:
            print(form.errors)
            print(formset.errors)
    return render(request, 'essays/form-essay_add.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_testfileessay', raise_exception=True)#type:ignore
@transaction.atomic
def editTestFileEssay (request, pk, tr, site, ck):
    
    obj = get_object_or_404(TestFileEssay, pk=pk)
    
    if obj.test_file.boot.test_request.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser): #type:ignore
        return render(request, 'errors/403.html', status=403)

    form = TestFileEssayForm(request.POST or None, instance=obj)
    formset = TestFileEssayResultFormset(request.POST or None, prefix='results', instance = obj)

    context = {'form': form,'formset': formset, 'segment':'test_request', 'set': 'edit', 'back': True}

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            test_request = form.save(commit=False)
            #validation
            test_request.save(force_update=True)

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

            if site == 'p':
                return redirect(f'/test_requests/{tr}/printer/{ck}')
            else:
                return redirect(f'/test_requests/{tr}/laminator/{ck}')
        else:
            print(formset.errors)
    return render(request, 'essays/form-essay_results.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_testfileessay', raise_exception=True)#type:ignore
def deleteTestFileEssay (request, pk):
    obj = TestFileEssay.objects.get(id=pk)

    if obj.test_file.boot.test_request.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser): #type:ignore
        return render(request, 'errors/403.html', status=403)

    obj.delete()
    return JsonResponse({'success': True})

@login_required(login_url='/login/')
@permission_required('essays.delete_bobbin', raise_exception=True)#type:ignore
def deleteBobbin (request, pk):

    obj = Bobbin.objects.get(id=pk)

    if obj.test_request.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    obj.delete()
    return JsonResponse({'success': True})
#----------------------------------------------------------------->

#Cutter Boot------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('essays.add_cutterboot', raise_exception=True)#type:ignore
def addCutterBootTR (request, tr):
    
    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the parent to render
    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    structure_list = TestStructure.objects.filter(test_request__pk=tr)
    tr_weight = 0
    for st in structure_list:
        tr_weight = tr_weight + st.weight #type:ignore

    form = CutterBootForm(request.POST or None)
    context = {'form': form, 'test_request_obj':test_request_obj, 'tr_weight':tr_weight, 'segment':'test_request', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            cutter_boot = form.save(commit=False)
            #validation
            cutter_boot.r_p = average(cutter_boot.r_a, cutter_boot.r_b, cutter_boot.r_c)
            cutter_boot.w_p = average(cutter_boot.w_a, cutter_boot.w_b, cutter_boot.w_c)
            cutter_boot.test_request = test_request_obj
            cutter_boot.save()

            test_request_obj.touched = True
            test_request_obj.production_order = request.POST.get('production_order')
            test_request_obj.save()
                
            return redirect(f'/test_requests/{test_request_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-cutter_boot.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_cutterboot', raise_exception=True)#type:ignore
def editCutterBootTR (request, tr, ck):

    test_request_obj = get_object_or_404(TestRequest, pk=tr)#Get the parent to render

    if test_request_obj.signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    cutter_boot_obj = get_object_or_404(CutterBoot, pk=ck)#Get the parent to render

    structure_list = TestStructure.objects.filter(test_request__pk=tr)
    tr_weight = 0
    for st in structure_list:
        tr_weight = tr_weight + st.weight #type:ignore

    form = CutterBootForm(request.POST or None, instance=cutter_boot_obj)
    context = {'form': form, 'test_request_obj':test_request_obj, 'tr_weight':tr_weight, 'segment':'test_request', 'back': True}
    
    if request.method == 'POST':
        if form.is_valid():
            cutter_boot = form.save(commit=False)
            #validation
            cutter_boot.r_p = average(cutter_boot.r_a, cutter_boot.r_b, cutter_boot.r_c)
            cutter_boot.w_p = average(cutter_boot.w_a, cutter_boot.w_b, cutter_boot.w_c)

            cutter_boot.test_request = test_request_obj
            
            cutter_boot.save()
            test_request_obj.touched = True
            test_request_obj.production_order = request.POST.get('production_order')
            test_request_obj.save()
            return redirect(f'/test_requests/{test_request_obj.id}/cutter/{cutter_boot_obj.id}') #type:ignore
        else:
            print(form.errors)
    return render(request, 'essays/form-cutter_boot.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_cutterboot', raise_exception=True)#type:ignore
def deleteCutterBootTR (request, tr, ck):

    if TestRequest.objects.get(pk = tr).signed_techspecs and not (request.user.groups.filter(name = 'ASCA-Staff').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    item = get_object_or_404(CutterBoot, pk=ck)
    if request.method == 'POST':
        item.delete()
    return redirect('view_test_request', tr)
#-------------------------------------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('essays.add_technicalspecs', raise_exception=True)#type:ignore
def addTechSpecs (request, tr):
    test_request_obj = get_object_or_404(TestRequest, pk=tr)
    form = TechnicalSpecsForm(request.POST or None)
    context = {'form': form, 'test_request_obj': test_request_obj, 'segment':'test_request', 'back': True}
    if request.method == 'POST':
        if form.is_valid():
            data = form.save(commit=False)
            data.test_request = test_request_obj
            
            data.save()

            test_request_obj.touched = True
            test_request_obj.save()
        else:
            print(form.errors)
        return redirect(f'/test_requests/{tr}/tech_specs')
    return render(request, 'essays/form-technical_specs.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_technicalspecs', raise_exception=True)#type:ignore
def editTechSpecs (request, tr, ck):
    test_request_obj = get_object_or_404(TestRequest, pk=tr)
    tech_specs_obj = get_object_or_404(TechnicalSpecs, pk=ck)
    form = TechnicalSpecsForm(request.POST or None, instance=tech_specs_obj)
    context = {'form': form, 'test_request_obj': test_request_obj, 'segment':'test_request', 'back': True}
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            test_request_obj.touched = True
            test_request_obj.save()
        else:
            print(form.errors)

        return redirect(f'/test_requests/{tr}/tech_specs')

    return render(request, 'essays/form-technical_specs.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_technicalspecs', raise_exception=True)#type:ignore
def deleteTechSpecs (request, tr, ck):
    item = get_object_or_404(TechnicalSpecs, pk=ck)
    if request.method == 'POST':
        item.delete()
        return redirect(f'/test_requests/{tr}/tech_specs')
        
    return redirect('view_test_request', tr)
#----------------------------------------------------------------->
#-------------------------------------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('essays.view_annex', raise_exception=True)#type:ignore
def viewAnnex(request, pk):
    test_request_obj = get_object_or_404(TestRequest, pk=pk)
    annexes = Annex.objects.filter(test_request__id=pk)
    
    structure_list = TestStructure.objects.filter(test_request__pk=pk)
    
    printer_boot = PrinterBoot.objects.filter(test_request__pk=pk)
    lamination_boot = LaminatorBoot.objects.filter(test_request__pk=pk)
    cutter_boot = CutterBoot.objects.filter(test_request__pk=pk)
    spec_extra = TechnicalSpecs.objects.filter(test_request=test_request_obj).first()
    annexes = Annex.objects.filter(test_request__pk=pk)

    content = 'essays/details/annex.html'
    
    context = {
        'test_request_obj':test_request_obj,
        'structure_list':structure_list,
        #'lamination_list':lamination_list,#DELETE_LATER
        'printer_boot':printer_boot,
        'lamination_boot':lamination_boot,
        'cutter_boot':cutter_boot,
        'spec_extra':spec_extra,
        'annexes':annexes,
        'segment':'test_request',
        'tab':'annex',
        'back': True,
        'content':content
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content_html = render_to_string(content, context, request)
        
        return JsonResponse({'content_html': content_html})
    
    return render(request, 'essays/details-test_request.html', context)

@login_required(login_url='/login/')
@permission_required('essays.add_annex', raise_exception=True)#type:ignore
def addAnnex(request, tr):
    test_request_obj = get_object_or_404(TestRequest, pk=tr)

    ug = request.user.groups

    if test_request_obj.signed_techspecs and not (ug.filter(name = 'ASCA-Staff').exists() or ug.filter(name = 'IDAT-A').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)
    
    number = "0"
    last_annex = Annex.objects.last()
    if last_annex:
        number = get_the_num(last_annex.image.name)
    context = {'test_request_obj': test_request_obj, 'segment':'test_request', 'back': True}
    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')

        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            context['message'] = 'Sólo se admiten imágenes en formato JPG o PNG'
            return render(request, 'essays/form-annex.html', context)

        image.name = rename_file(image.name, number)

        try:
            img = Image.open(image)
            img = ImageOps.exif_transpose(img)

            if isinstance(img, JpegImagePlugin.JpegImageFile):
                img.info.pop('exif', None)

        except IOError:
            context['message'] = 'El archivo no es una imagen válida o está dañado'
            return render(request, 'essays/form-annex.html', context)


        max_size = (2000, 2000)
        img.thumbnail(max_size) # type: ignore

        output = BytesIO()
        img = img.convert("RGB") #type:ignore
        img.save(output, format='JPEG', quality=30)

        output.seek(0)

        image = File(output, name=image.name)

        Annex.objects.create(
            test_request=test_request_obj,
            identification=data['identification'],
            image=image,
            )
        #test_request_obj.touched = True #DELETE_LATER
        #test_request_obj.save() #DELETE_LATER
        return redirect('view_annexes', tr)
    
    return render(request, 'essays/form-annex.html', context)

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
def deleteAnnex (request, tr, ck):
    item = get_object_or_404(Annex, pk=ck)

    test_request_obj = get_object_or_404(TestRequest, pk=tr)
    ug = request.user.groups

    if test_request_obj.signed_techspecs and not (ug.filter(name = 'ASCA-Staff').exists() or ug.filter(name = 'IDAT-A').exists() or request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        item.delete()
    return redirect('view_annexes', tr)

def error_message(data):
    return data
#----------------------------------------------------------------->
    
#Personal Model crud------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('essays.view_personal', raise_exception=True)
def indexPersonal(request, set):
    
    if set == 'a':
        obj = QualityAnalyst.objects.all().order_by('name')
        segment = 'analysts'
        url = '/analyst/'
        title = 'Analistas de Calidad'
    else:
        obj = ProductionOperator.objects.all().order_by('name')
        segment = 'operators'
        url = '/operator/'
        title = 'Operadores de Producción'
 
    search_text = request.GET.get('search_text')
    if search_text:
        obj = obj.filter(Q(name__icontains=search_text))

    paginator = Paginator(obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    objects = paginator.get_page(page_number)
    table = 'essays/tables/personal.html'

    context = {
        'objects':objects,
        'segment':segment,
        'url':url,
        'table':table,
        'set':set,
        'title':title,
        'search':True
        }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('essays/tables/personal.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'essays/tables-personal.html', context)

@login_required(login_url='/login/')
@permission_required('essays.add_personal', raise_exception=True)
def addQualityAnalyst(request):

    form = QualityAnalystForm()
    if request.method == 'POST':
        form = QualityAnalystForm(request.POST)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('personal', 'a')

    context ={
        'form':form,
        'segment':'analysts',
        'title':'Analista de Calidad',
        'back':True
        }
    return render(request, 'essays/form-personal.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_personal', raise_exception=True)
def editQualityAnalyst(request, pk):

    obj = QualityAnalyst.objects.get(id = pk)
    form = QualityAnalystForm(instance = obj)
    if request.method == 'POST':
        form = QualityAnalystForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('personal', 'a')

    context = {
        'form':form,
        'segment':'analysts',
        'title':'Analista de Calidad',
        'back':True
        }

    return render(request, 'essays/form-personal.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_personal', raise_exception=True)#type:ignore
def deleteQualityAnalyst(request, pk):
    obj = QualityAnalyst.objects.get(id = pk)    
    if request.method == 'POST':
        obj.delete()
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    return redirect('personal', 'a')
    
@login_required(login_url='/login/')
@permission_required('essays.add_personal', raise_exception=True)
def addProductionOperator(request):

    form = ProductionOperatorForm()
    if request.method == 'POST':
        form = ProductionOperatorForm(request.POST)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('personal', 'o')

    context ={
        'form':form,
        'segment':'operators',
        'title':'Operador de Producción',
        'back':True
        }
    return render(request, 'essays/form-personal.html', context)

@login_required(login_url='/login/')
@permission_required('essays.change_personal', raise_exception=True)
def editProductionOperator(request, pk):

    obj = ProductionOperator.objects.get(id = pk)
    form = ProductionOperatorForm(instance = obj)
    if request.method == 'POST':
        form = ProductionOperatorForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('personal', 'o')

    context = {
        'form':form,
        'segment':'operators',
        'title':'Operador de Producción',
        'back':True
        }

    return render(request, 'essays/form-personal.html', context)

@login_required(login_url='/login/')
@permission_required('essays.delete_personal', raise_exception=True)#type:ignore
def deleteProductionOperator(request, pk):
    obj = ProductionOperator.objects.get(id = pk)    
    if request.method == 'POST':
        obj.delete()
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    return redirect('personal', 'o')
