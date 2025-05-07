import datetime, re
from io import BytesIO
from pytz import timezone as tz
from datetime import date, datetime
from django.db import transaction 
from django.http import JsonResponse
from django.forms import modelformset_factory
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files import File
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

#app imports------------------------------------------------------->
#from .filters import *
from .models import *
from .forms import *
from apps.production.models import Order, PrinterBoot, LaminatorBoot, CutterBoot
from apps.home.models import Plan, Structure, DeincorporateRequest
from apps.graphics.models import PrePrint

class SaleOrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    permission_required = 'sales.view_saleorder'
    model = SaleOrder
    template_name = 'sales/tables-sale_order_qp.html'
    ordering = ['-representative__number', '-request']
    context_object_name = 'objects'
    paginate_by = 15
    orphans = 2

    def get(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        treview = bool(self.request.GET.get('treview', None))
        rejected = bool(self.request.GET.get('rejected', None))
        archive = bool(self.request.GET.get('archive', None))
        deleted = bool(self.request.GET.get('deleted', None))

        if rejected:
            self.object_list = self.object_list.filter(Q(archived=False)&Q(deleted=False)&Q(treview__approved=False))
            self.extra_context = {'tab': 'rejected', 'segment':'review_sale_orders'}
        elif treview:
            self.object_list = self.object_list.filter(Q(archived=False)&Q(deleted=False)&Q(treview__approved=None))
            self.extra_context = {'tab': 'treview', 'segment':'review_sale_orders'}
        elif archive:
            self.object_list = self.object_list.filter(archived=True)
            self.extra_context = {'tab': 'archive'}
        elif deleted:
            self.object_list = self.object_list.filter(deleted=True)
            self.extra_context = {'tab': 'deleted'}
        else:
            self.object_list = self.object_list.filter(Q(archived=False)&Q(deleted=False)&Q(treview__approved=True))#&Q(treview=False or None)
            
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Pedidos'
        context['segment'] = 'sale_orders'
        context['tab'] = 'main'
        context['table'] = 'sales/tables/sale_order.html'
        context['search'] = True
        if self.extra_context is not None:
            context.update(self.extra_context)
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_text = self.request.GET.get('search_text', None)
        archive = self.request.GET.get('archive', None)
        deleted = self.request.GET.get('deleted', None)
        if search_text:
            queryset = queryset.filter(
                Q(plan__product__icontains=search_text)|
                Q(plan__client__name__icontains=search_text)|
                Q(request__icontains=search_text)|
                Q(number__icontains=search_text)|
                Q(representative__number__icontains=search_text)|
                Q(representative__name__icontains=search_text)|
                Q(request_date__icontains=search_text)
            )
        if archive:
            queryset = queryset.filter(archived=True)
        elif deleted:
            queryset = queryset.filter(deleted=True)
        else:
            queryset = queryset.filter(Q(archived=False)&Q(deleted=False))

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table_html = render_to_string('sales/tables/sale_order.html', context, request=self.request)
            paginator_html = render_to_string('includes/paginator.html', context, request=self.request)
            return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        else:
            return super().render_to_response(context, **response_kwargs)


class SaleOrderDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    login_url = '/login/'
    permission_required = 'sales.view_saleorder'
    model = SaleOrder
    template_name = 'sales/view-sale_order.html'  # replace with your template
    context_object_name = 'sale_order'
    content = 'sales/details/sale_order.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.archived or obj.deleted:#type:ignore
            if not self.request.user.has_perm('sales.view_archive_purchsae_order'):#type:ignore
                raise Http404("No SaleOrder matches the given query.")#type:ignore
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_order = self.get_object()
        plan_instance = sale_order.plan #type:ignore
        reference_date = sale_order.reference_date #type:ignore

        # Fetch the historical record of Plan closest to but not after the reference_date
        plan = plan_instance.history.as_of(reference_date)
        if not plan:
            plan = plan_instance

        # Fetch the historical records of Structure related to the historical Plan closest to but not after the reference_date
        structures = Structure.history.as_of(reference_date).filter(plan_id=plan.id).order_by('id') #type:ignore

        # If there are no historical records before the reference_date, use the current structures
        if not structures.exists():
            structures = plan_instance.structure_set.all()

        if not sale_order.treviewed:  # type:ignore
            context['segment'] = 'treview'
        else:
            context['segment'] = 'sale_orders'
        
        context['detail'] = 'sale_order'

        if self.request.GET.get('production_file', None):
            context['order_obj'] = Order.objects.filter(sale_order=sale_order).first()
            context['printer_boot'] = PrinterBoot.objects.filter(production_order = context['order_obj'])
            context['laminator_boot'] = LaminatorBoot.objects.filter(production_order = context['order_obj'])
            context['cutter_boot'] = CutterBoot.objects.filter(production_order = context['order_obj'])
            context['segment']= 'order'
            context['detail']='production'
            self.template_name = 'production/details-production.html'
        context['back'] = True
        context['tab'] = 'parent'
        # Add plan and structures to the context
        context['plan'] = plan
        context['structures'] = structures
        context['content'] = self.content
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            content_html = render_to_string(self.content, context, self.request)
            return JsonResponse({'content_html': content_html})
        else:
            return super().render_to_response(context, **response_kwargs)
        
@login_required(login_url='/login/')
@permission_required('sales.add_saleorder', raise_exception=True)
def addSaleOrderQP(request, pk):

    plan = get_object_or_404(Plan, pk=pk)
    structure_list = Structure.objects.filter(plan__pk=pk)
    representatives = Representative.objects.all()

    form = SaleOrderForm(request.POST or None, user=request.user)
    formset = DeliveryDateFormset(request.POST or None, prefix='dates')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            sale_order = form.save(commit=False)        
            sale_order.plan = plan

            if not sale_order.request:
                try:
                    last = SaleOrder.objects.filter(Q(representative=sale_order.representative)&Q(deleted=False)&(Q(treview__approved=True)|Q(treview=None))).order_by('-request')[0]
                    sale_order.request = set_number(int(last.request)) #type:ignore
                except:
                    sale_order.request = 1

            sale_order.save()

            dform = formset.save(commit=False)
            for date in dform:
                date.sale_order = sale_order
                
                date.save()

            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('sale_order_list')
        else:
            print(form.errors)
            print(formset.errors)
        
    context ={
        'form':form,
        'formset':formset,
        'plan':plan,
        'structure_list':structure_list,
        'representatives':representatives,
        'segment':'sale_orders',
        'title':'Pedido'
    }
    return render(request, 'sales/form-sale_order_qp.html', context)

@login_required(login_url='/login/')
@permission_required('sales.change_saleorder', raise_exception=True)
@transaction.atomic
def editSaleOrderQP(request, pk):
    
    if 'suggest' in request.GET:
        sale_order_review = SaleOrderReview.objects.get(pk=pk)
        sale_order = SaleOrder.objects.get(pk=sale_order_review.sale_order.id)#type:ignore
        plan = sale_order_review.suggested_replace

    else:
        sale_order_review = False
        sale_order = get_object_or_404(SaleOrder, pk=pk)
        plan = sale_order.plan


    structure_list = Structure.objects.filter(plan=plan)
    representatives = Representative.objects.all()

    form = SaleOrderForm(request.POST or None, instance=sale_order)
    formset = DeliveryDateFormset(request.POST or None, prefix='dates', instance=sale_order)
    ur_check = True

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            sale_order = form.save(commit=False)
            sale_order.plan = plan
            
            if request.POST.get('update_reference'):
               sale_order.reference_date = timezone.now() 

            if not sale_order.request:
                try:
                    last = SaleOrder.objects.filter(Q(representative=sale_order.representative)&Q(deleted=False)).exclude(pk=pk).order_by('-request')[0]
                    sale_order.request = set_number(int(last.request)) #type:ignore
                except:
                    sale_order.request = 1


            sale_order.save(force_update=True)

            for form in formset.deleted_forms:
                form.instance.delete()

            formset.save()

            if sale_order_review:
                sale_order_review.delete()
                return redirect('/sale_orders/?treview=True') 

            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('sale_order_list') 
        else:
            print(form.errors)
            print(formset.errors)
        
    context ={
        'form':form,
        'formset':formset,
        'plan':plan,
        'sale_order':sale_order,
        'ur_check':ur_check,
        'structure_list':structure_list,
        'representatives':representatives,
        'segment':'sale_orders',
        'title':'Pedido'
    }
    return render(request, 'sales/form-sale_order_qp.html', context)

def set_number(val: int) -> str:
    number = val + 1
    return f"{number}"

def get_delivery_addresses(request):
    client = request.GET.get('client')
    addresses = DeliveryAddress.objects.filter(client=client).values()
    return JsonResponse(list(addresses), safe=False)

@login_required(login_url='/login/')
@permission_required('sales.archive_sale_order', raise_exception=True)#type:ignore
def archiveSaleOrderQP(request, pk):

    obj = get_object_or_404(SaleOrder, pk=pk)
    
    obj.archived = True
    obj.save()

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('sale_order_list')

@login_required(login_url='/login/')
@permission_required('sales.archive_sale_order', raise_exception=True)#type:ignore
def unarchiveSaleOrderQP(request, pk):

    obj = get_object_or_404(SaleOrder, pk=pk)
    
    obj.archived = False
    obj.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('sale_order_list')

@login_required(login_url='/login/')
@permission_required('sales.delete_saleorder', raise_exception=True)#type:ignore
def deleteSaleOrderQP(request, pk):

    obj = get_object_or_404(SaleOrder, pk=pk)
    
    
    obj.deleted_by = request.user.username
    obj.deleted_time = timezone.now()
    obj.deleted = True
    obj.save()

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect('sale_order_list')

@login_required(login_url='/login/')
@permission_required('sales.restore_deleted_sale_order', raise_exception=True)#type:ignore
def restoreSaleOrderQP(request, pk):

    obj = get_object_or_404(SaleOrder, pk=pk)
    
    obj.deleted = False
    obj.save()
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    return redirect('sale_order_list')

@login_required(login_url='/login/')
@permission_required('sales.delete_deleted_sale_order', raise_exception=True)#type:ignore
def deleteTrueSaleOrderQP(request, pk):

    obj = get_object_or_404(SaleOrder, pk=pk)
    
    if request.method == 'POST':
        obj.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('sale_order_list')

@login_required(login_url='/login/')
@permission_required('sales.add_saleorderreview', raise_exception=True)
@csrf_protect
def review_sale_order(request):

    splan = None
    full_name = f'{request.user.first_name or ""} {request.user.last_name or ""}'.strip()

    if request.POST.get('suggested_replace'):
        splan = Plan.objects.get(pk=request.POST.get('suggested_replace'))

    review = SaleOrderReview.objects.create(
        sale_order = SaleOrder.objects.get(pk=request.POST.get('sale_order')),
        approved = bool(request.POST.get('approved')),
        deincorporate_request = bool(request.POST.get('deincorporate')),
        suggested_replace = splan,
        observation = request.POST.get('observation'),
        by = full_name
    )
    
    if request.POST.get('deincorporate') and request.POST.get('plan'):
        plan = Plan.objects.get(pk=request.POST.get('plan'))
        time = timezone.now()

        if request.POST.get('observation'):
            motive = f"Bajo el motivo - {request.POST.get('observation')}."
        else:
            motive = 'Sin especificar un motivo.'

        DeincorporateRequest.objects.create(
            review = review,
            plan = plan,
            description = f"En la fecha {time.strftime('%d/%b/%Y').upper()} a las {time.astimezone(tz('America/Caracas')).strftime('%H:%M')} horas, {full_name} solicita la deseincorporación del plan de calidad PC-ASC-{plan.pc} - {plan.product} {motive}"
        )

    return JsonResponse({'status':'success', 'message': 'Éxito'})

@login_required(login_url='/login/')
@permission_required('sales.delete_saleorderreview', raise_exception=True)
@csrf_protect
def return_review_sale_order(request, pk):

    review = get_object_or_404(SaleOrderReview, pk=pk)
    review.delete()

    return JsonResponse({'status':'success', 'message': 'Éxito'})

#Sales Test Request
@login_required(login_url='/login/')
@permission_required('sales.view_salestestrequest', raise_exception=True)
def indexSalesTestRequest(request):
    
    sales_test_request_obj = SalesTestRequest.objects.all().order_by('date')

    search_text = request.GET.get('search_text')
    if search_text:
        sales_test_request_obj = sales_test_request_obj.filter(Q(client__name__icontains=search_text)|Q(product__icontains=search_text))
   
    paginator = Paginator(sales_test_request_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    sales_test_request_list = paginator.get_page(page_number)

    context={
        'objects' : sales_test_request_list,
        'table':'sales/tables/sales_test_request.html',
        'segment':'sales_test_request',
        'tab':'sales_test_requests',
        'search':True
        }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('sales/tables/sales_test_request.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        
    return render(request, 'sales/tables-sales_test_requests.html', context)

@login_required(login_url='/login/')
@permission_required('sales.add_salestestrequest', raise_exception=True)
@transaction.atomic
def addSalesTestRequest(request):
    if request.method == 'POST':
        form = SalesTestRequestForm(request.POST, request.FILES)
        formset = SalesStructureFormset(request.POST, prefix='structures')
        if form.is_valid() and formset.is_valid():
            s_test_request = form.save()

            structures = formset.save(commit=False)
            for structure in structures:
                structure.s_test_request = s_test_request
                structure.save()

            response_data = {
                'success': True,
                'message': 'Sales Test Request created successfully.',
                'url': '/sales_test_requests/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            formset_errors = formset.errors
            response_data = {
                'success': False,
                'form_errors': errors,
                'formset_errors': formset_errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = SalesTestRequestForm()
        formset = SalesStructureFormset(prefix='structures')
        context = {
            'form': form,
            'formset': formset,
            'segment': 'sales_test_request',
            'back': True
        }
        return render(request, 'sales/form-sales_test_request.html', context)

@login_required(login_url='/login/')
@permission_required('sales.change_salestestrequest', raise_exception=True)
@transaction.atomic
def editSalesTestRequest(request, pk):

    sales_test_request = SalesTestRequest.objects.get(pk = pk)

    if request.method == 'POST':
        form = SalesTestRequestForm(request.POST, request.FILES, instance=sales_test_request)
        formset = SalesStructureFormset(request.POST, prefix='structures', instance=sales_test_request)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            response_data = {
                'success': True,
                'message': 'Sales Test Request created successfully.',
                'url': '/sales_test_requests/'
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            formset_errors = formset.errors
            response_data = {
                'success': False,
                'form_errors': errors,
                'formset_errors': formset_errors,
            }
            return JsonResponse(response_data, status=400)
    else:
        form = SalesTestRequestForm(instance=sales_test_request)
        formset = SalesStructureFormset(prefix='structures', instance=sales_test_request)
        context = {
            'object':sales_test_request,
            'form': form,
            'formset': formset,
            'segment': 'sales_test_request',
            'back': True
        }
        return render(request, 'sales/form-sales_test_request.html', context)

@login_required(login_url='/login/')
@permission_required('sales.delete_salestestrequest', raise_exception=True)#type:ignore
def deleteSalesTestRequest(request, pk):

    sales_test_request = SalesTestRequest.objects.get(pk = pk)
    
    if request.method == 'POST':
        sales_test_request.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('/sales_test_requests/')
