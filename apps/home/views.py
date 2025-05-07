# -*- encoding: utf-8 -*-

# Copyright (c) 2022 - present Daniel Escalona
from enum import Flag
import decimal, os
import time
from django.db import transaction, connection
from django.urls import reverse
from django.core import serializers
from django.http import HttpRequest, JsonResponse, FileResponse, Http404
from django.utils import timezone
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.test.utils import CaptureQueriesContext
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
#app imports------------------------------------------------------->
from .filters import *
from .models import *
from .forms import *
from .utils import *

def get_id(model):
    existing_ids = set(model.objects.values_list('id', flat=True))
    if existing_ids:
        max_existing_id = max(existing_ids)
        for i in range(1, max_existing_id + 2):
            if i not in existing_ids:
                return i
    else:
        return 0
    
def success(*args):
    for arg in args:
        success = f'{arg} is True'
        #success.save()
    return HttpRequest

@login_required(login_url='/login/')
def index(request):    
    return redirect('clients')

@login_required
def protected_serve(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        raise Http404
#Model Index---------------------------------------------------------->

#Plan
def indexPlans(request):
    header = request.GET.get('header') or 'plans'
    plan_obj = Plan.objects.all()

    if header == 'plans':
        plan_obj = plan_obj.exclude(archived=True).exclude(disincorporated=True).exclude(pc='00000000').order_by('pc', 'client', 'product', '-date_created')
        deincorporate_requests = DeincorporateRequest.objects.filter(rejected=False)
    elif header == 'plans-0':
        plan_obj = plan_obj.exclude(archived=True).exclude(disincorporated=True).filter(pc='00000000').order_by('pc', 'client', 'product', '-date_created')
        if 'reviewer_none' in request.GET:
            plan_obj = plan_obj.filter(Q(reviewer=None)|Q(reviewer='')).order_by('pc', 'client', 'product', '-date_created')
    elif header == 'deleted':
        plan_obj = plan_obj.filter(archived=True).order_by('-delete_time', 'pc', 'client', 'product')
    elif header == 'disincorporated':
        plan_obj = plan_obj.filter(disincorporated=True).exclude(archived=True).order_by('-disicomop_time', 'pc', 'client', 'product')

    search_text = request.GET.get('search_text')
    if search_text:
        plan_obj = plan_obj.filter(Q(product__icontains=search_text)|Q(gp_code__icontains=search_text)|Q(code__icontains=search_text)|Q(pc__icontains=search_text)|Q(client__name__icontains=search_text))

    plan_filter = PlanFilter(request.GET, queryset=plan_obj)
    plan_obj = plan_filter.qs
        
    paginator = Paginator(plan_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    plan_list = paginator.get_page(page_number)

    table = 'home/tables/plan.html'

    context = {
        'objects': plan_list,
        'plan_filter': plan_filter,
        'table': table,
        'segment': 'plan',
        'tab': header,
        'search': True
    }

    if header == 'plans':
        context['deincorporate_requests'] = deincorporate_requests

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        header_html = render_to_string('home/headers/plan.html', context, request)
        table_html = render_to_string(table, context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'header_html': header_html, 'table_html': table_html, 'paginator_html': paginator_html})

    return render(request, 'home/tables-plans.html', context)

@login_required(login_url='/login/')
def viewPlan(request, pk):

    plan_details = get_object_or_404(Plan, pk=pk)
    structure_list = Structure.objects.filter(plan__pk=pk)
    test_list = Test.objects.filter(plan__pk=pk)

    if plan_details.pc == '00000000' and not request.user.has_perm('home.add_plan'):
        return render(request, 'errors/404.html', status=404)
    if plan_details.archived and not request.user.has_perm('home.view_archive_plan'):
        return render(request, 'errors/404.html', status=404)
    if plan_details.disincorporated and not request.user.has_perm('home.view_disincorporate_plan'):
        return render(request, 'errors/404.html', status=404)

    ink = []
    ink_c = 0
    adh = []
    adh_c = 0
    res = []
    res_c = 0
    sil = []
    sil_c = 0
    lac = []
    lac_c = 0
    par = []
    par_c = 0
    bar = []
    bar_c = 0
    pri = []
    pri_c = 0
    cer = []
    cer_c = 0
    com = []
    com_c = 0
    
    for n in structure_list:
                
        if n.material_type.name.startswith('Tintas'): #type:ignore
            ink.append(n.weight)
            ink_c+=1

        if n.material_type.name.startswith('Adhesivo'): #type:ignore
            adh.append(n.weight)
            adh_c+=1
        
        if n.material_type.name.startswith('Resina'): #type:ignore
            res.append(n.weight)
            res_c+=1
        
        if n.material_type.name.startswith('Silicona'): #type:ignore
            sil.append(n.weight)
            sil_c+=1

        if n.material_type.name.startswith('Laca'): #type:ignore
            lac.append(n.weight)
            lac_c+=1
        
        if n.material_type.name.startswith('Parafina'): #type:ignore
            par.append(n.weight)
            par_c+=1
        
        if n.material_type.name.startswith('Barniz'): #type:ignore
            bar.append(n.weight)
            bar_c+=1

        if n.material_type.name.startswith('Primer'): #type:ignore
            pri.append(n.weight)
            pri_c+=1

        if n.material_type.name.startswith('Cera'): #type:ignore
            cer.append(n.weight)
            cer_c+=1
        if n.material_type.name.startswith('Compuesto'): #type:ignore
            com.append(n.weight)
            com_c+=1

    context={
        'plan_details':plan_details,
        'structure_list':structure_list,
        'test_list':test_list,
        'segment':'plan',
        'ink': ink,
        'ink_c': ink_c,
        'adh': adh,
        'adh_c': adh_c,
        'res': res,
        'res_c': res_c,
        'par': par,
        'par_c': par_c,
        'sil': sil,
        'sil_c': sil_c,
        'lac': lac,
        'lac_c': lac_c,
        'bar': bar,
        'bar_c': bar_c,
        'pri': pri,
        'pri_c': pri_c,
        'cer': cer,
        'cer_c': cer_c,
        'com': com,
        'com_c': com_c,
        'back': True,
    }    
    
    return render(request, 'home/plan_view.html', context)

#Client
@login_required(login_url='/login/')
@permission_required('home.view_client', raise_exception=True)
def indexClient(request):
    
    client_obj = Client.objects.all().order_by('name')

    search_text = request.GET.get('search_text')
    if search_text:
        client_obj = client_obj.filter(Q(rif_num__icontains=search_text)|Q(rif_type__icontains=search_text)|Q(name__icontains=search_text))
   
    paginator = Paginator(client_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    client_list = paginator.get_page(page_number)

    context={
        'objects' : client_list,
        'table':'home/tables/client.html',
        'segment':'client',
        'tab':'clients',
        'search':True
        }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('home/tables/client.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
        
    return render(request, 'home/tables-clients.html', context)

#Provider
@login_required(login_url='/login/')
@permission_required('home.view_provider', raise_exception=True) 
def indexProviders(request):

    provider_obj = Provider.objects.all().order_by('name')

    search_text = request.GET.get('search_text')
    if search_text:
        provider_obj = provider_obj.filter(Q(name__icontains=search_text))

    paginator = Paginator(provider_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    provider_list = paginator.get_page(page_number)

    context={
        'objects' : provider_list,
        'table':'home/tables/provider.html',
        'segment':'provider',
        'tab':'providers',
        'search':True
        }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('home/tables/provider.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'home/tables-providers.html', context)

#Material

@login_required(login_url='/login/')
@permission_required('home.view_material', raise_exception=True)
def ajaxMaterials(request):
    query = request.GET.get('q', None)
    filtr = request.GET.get('f', None)
    provider = request.GET.get('p', None)
    if not query and not provider:
        return JsonResponse(data={'success': False, 'errors': 'Seleccione un tipo de material'})
    if provider:
        materials_obj = Material.objects.filter(provider__pk=provider).values("pk", "name", "provider__name", "material_type__name")
    else:
        materials_obj = Material.objects.filter(material_type=query).values("pk", "name", "provider__name", "material_type__name")
    if filtr:
        materials_obj = materials_obj.filter(Q(name__icontains=filtr)|Q(provider__name__icontains=filtr))
    materials = list(materials_obj)
    return JsonResponse(materials, safe=False)

@login_required(login_url='/login/')
@permission_required('home.view_material', raise_exception=True)
def indexMaterials(request):

    material_obj = Material.objects.all().order_by('material_type__name', 'provider__name', 'name')

    search_text = request.GET.get('search_text')
    if search_text:
        material_obj = material_obj.filter(Q(material_type__name__icontains=search_text)|Q(provider__name__icontains=search_text)|Q(name__icontains=search_text))

    paginator = Paginator(material_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    material_list = paginator.get_page(page_number)    
    
    context={
        'objects':material_list,
        'table':'home/tables/material.html',
        'segment':'material',
        'tab':'materials',
        'search':True,
        }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('home/tables/material.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'home/tables-materials.html', context)

#Material Type
@login_required(login_url='/login/')
def ajaxMaterialTypes(request):
    filtr = request.GET.get('f', None)
    
    materials = MaterialType.objects.all()
    if filtr:
        materials = materials.filter(Q(name__icontains=filtr))
    materials_json = serializers.serialize('json', materials)
    
    return JsonResponse(materials_json, safe=False)

#Providers
@login_required(login_url='/login/')
def ajaxProviders(request):
    filtr = request.GET.get('f', None)

    providers = Provider.objects.all()
    if filtr:
        providers = providers.filter(Q(name__icontains=filtr))

    providers_json = serializers.serialize('json', providers)
    return JsonResponse(providers_json, safe=False)

@login_required(login_url='/login/')
@permission_required('home.view_materialtype', raise_exception=True)
def indexMaterialTypes(request):

    mat_type_obj = MaterialType.objects.all().order_by('name')
 
    search_text = request.GET.get('search_text')
    if search_text:
        mat_type_obj = mat_type_obj.filter(Q(name__icontains=search_text))

    paginator = Paginator(mat_type_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    material_list = paginator.get_page(page_number)   

    context = {
        'objects':material_list,
        'table':'home/tables/material_type.html',
        'segment':'material',
        'tab':'material_types',
        'search':True
        }    
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('home/tables/material_type.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'home/tables-material_types.html', context)

#Essay
@login_required(login_url='/login/')
@permission_required('home.view_essay', raise_exception=True)
def indexEssays(request):

    essay_obj = Essay.objects.all().order_by('method', 'name')
    
    search_text = request.GET.get('search_text')
    if search_text:
        essay_obj = essay_obj.filter(Q(method__icontains=search_text)|Q(name__icontains=search_text)|Q(detail__icontains=search_text)|Q(unit__name__icontains=search_text)|Q(unit__description__icontains=search_text))

    paginator = Paginator(essay_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    essay_list = paginator.get_page(page_number)    

    context={
        'objects':essay_list,
        'table':'home/tables/essay.html',
        'segment':'essay',
        'tab':'essays',
        'search':True,
        }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('home/tables/essay.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'home/tables-essays.html', context)

#Unit
@login_required(login_url='/login/')
@permission_required('home.view_unit', raise_exception=True)
def indexUnits(request):

    unit_obj = Unit.objects.all().order_by('name')
 
    search_text = request.GET.get('search_text')
    if search_text:
        unit_obj = unit_obj.filter(Q(description__icontains=search_text)|Q(name__icontains=search_text)|Q(symbol__icontains=search_text))

    paginator = Paginator(unit_obj, per_page=15, orphans=2)
    page_number = request.GET.get('page')
    unit_list = paginator.get_page(page_number)

    context = {
        'objects':unit_list,
        'table':'home/tables/unit.html',
        'segment':'essay',
        'tab':'units',
        'search':True
        }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('home/tables/unit.html', context, request)
        paginator_html = render_to_string('includes/paginator.html', context, request)
        return JsonResponse({'table_html': table_html, 'paginator_html': paginator_html})
    
    return render(request, 'home/tables-units.html', context)
#--------------------------------------------------------------------->

#Plan Model crud------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('home.add_plan', raise_exception=True)
@transaction.atomic
def PlanCreate(request):

    form = PlanForm(request.POST or None, initial={'format': '2'})
    sformset = StructureFormset(request.POST or None, queryset=Structure.objects.none(), prefix='structures')
    tformset = TestFormset(request.POST or None, queryset=Test.objects.none(), prefix='tests')

    context = {
        'form': form,
        'sformset': sformset,
        'tformset': tformset,
        'segment':'plan'
    }

    if request.method == 'POST':

        if form.is_valid() and sformset.is_valid() and tformset.is_valid():
            
            plan = form.save(commit=False)
            
            plan.gp_code = plan.gp_code.upper()
            plan.code = plan.code.upper()

            if request.user.has_perm('home.change_plan'):
                plan.pc = plan.pc.upper()
            else:
                plan.pc = '00000000'

            if not request.user.has_perm('home.sign_plan'):
                plan.reviewer = None

            plan.id = get_id(Plan)
            plan.save()

            splan = sformset.save(commit=False)

            for spn in splan:
                spn.plan = plan

            for strc in sformset:
                mat = strc.cleaned_data.get('material')
                stc = strc.save()

                for m in mat: #type:ignore
                    stc.material.add(m)

            tform = tformset.save(commit=False)
            new_tests = []
            for test in tform:
                test.plan = plan
                new_tests.append(test)

            Test.objects.bulk_create(new_tests)
            if request.POST.get('save_and_view'):
                return redirect('plan_view', plan.id)
            return redirect(reverse('plans') + '?header=plans-0')

    return render(request, 'home/plan_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.add_plan', raise_exception=True)
@transaction.atomic
def PlanUpdate(request, pk):

    obj = get_object_or_404(Plan, pk=pk)

    #Load Validation-----------------------------------------------
    has_change_plan = request.user.has_perm('home.change_plan')
    has_sign_plan = request.user.has_perm('home.sign_plan')

    if obj.archived or \
   (request.user.username == 'Pasante' and not obj.new_p) or \
   (not has_change_plan and obj.pc != '00000000') or \
   (obj.reviewer and not has_sign_plan):
        return render(request, 'errors/403.html', status=403)
    #--------------------------------------------------------------

    form = PlanForm(request.POST or None, instance=obj)
    sformset = StructureFormset(request.POST or None, instance = obj, prefix='structures')
    tformset = TestFormset(request.POST or None, instance = obj, prefix='tests')

    context = {'form': form, 'sformset': sformset, 'tformset': tformset,'segment':'plan', 'back':True}

    if request.method == 'POST':

        if form.is_valid() and sformset.is_valid() and tformset.is_valid():
            
            plan = form.save(commit=False)
            #validation-----------------------------------------
            if has_change_plan:
                plan.pc = plan.pc.upper()
            else:
                plan.pc = '00000000'
            if not has_sign_plan:
                plan.reviewer = None
            
            plan.gp_code = plan.gp_code.upper()
            plan.code = plan.code.upper()
            #end_validation-----------------------------------------
            plan.save(force_update=True)

            sformset.save()
            tformset.save()
            action = bool(request.POST.get('save_and_view'))
            if action == True:
                return redirect('plan_view', plan.id)
            if 'next' in request.GET:
                if plan.disincorporated == True:
                    return redirect(request.GET.get('next') + '&header=disincorporated')
                if plan.pc == '00000000':
                    return redirect(request.GET.get('next') + '&header=plans-0')
                return redirect(request.GET.get('next'))
            return redirect('plans')#save_and_view

    return render(request, 'home/plan_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.add_plan', raise_exception=True)
@transaction.atomic
def clonePlan(request, pk):
    with CaptureQueriesContext(connection) as context:

        plan = Plan.objects.get(id=pk)
        structure = Structure.objects.filter(plan__pk=pk).prefetch_related('material')
        test = Test.objects.filter(plan__pk=pk)

        plan.id = get_id(Plan) #type:ignore
        plan.archived = False
        plan.deleted_by = None
        plan.deleted_reason = None
        plan.delete_time = None
        plan.disincorporated = False
        plan.disicomop_by = None
        plan.disicomop_reason = None
        plan.disicomop_time = None
        plan.pc = '00000000'
        plan.code = '0000000000000'
        plan.elaborator = None
        plan.reviewer = None
        plan.product = f'Duplicado - {plan.product}'

        plan.save_no_history()

        for st in structure:
            mat = st.material
            st.id = None #type:ignore
            st.plan = plan #type:ignore
            st.save()
            for m in mat.all():
                st.material.add(m)        

        new_tests = []
        for ts in test:
            ts.id = None #type:ignore
            ts.plan = plan #type:ignore
            new_tests.append(ts)

        Test.objects.bulk_create(new_tests)
        #print(f"The function made {len(context)} queries.")

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect(reverse('plans') + '?header=plans-0')

@login_required(login_url='/login/')
@permission_required('home.disincorporate_plan', raise_exception=True)
def disincorporatePlan(request, pk):

    plan = Plan.objects.get(id=pk)
    
    plan.disincorporated = True
    plan.disicomop_reason = request.POST.get('disincorporate_reason')
    plan.disicomop_by = request.user.username
    plan.disicomop_time = timezone.now()

    if request.POST.get('disincorporate_request'):
        req = get_object_or_404(DeincorporateRequest, pk = int(request.POST.get('disincorporate_request')))
        req.delete()
        
    plan.save()

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect(reverse('plans') + '?header=disincorporated')

@login_required(login_url='/login/')
@permission_required('home.disincorporate_plan', raise_exception=True)
def rejectdisincorporatePlanRequest(request, pk):
    if request.POST.get('disincorporate_request'):
        req = get_object_or_404(DeincorporateRequest, pk = int(request.POST.get('disincorporate_request')))
        req.rejected = True
        req.save()
        return redirect('plans') 
    return render(request, 'errors/403.html', status=403)

@login_required(login_url='/login/')
@permission_required('home.disincorporate_plan', raise_exception=True)
def disincorporatePlanRequest(request, pk):

    obj = DeincorporateRequest.objects.get(id=pk)

    return render(request, 'home/deincorporate_request_form.html', context = {'obj':obj, 'segment':'plans'}) 

@login_required(login_url='/login/')
@permission_required('home.add_plan', raise_exception=True)
def deletePlan(request, pk):

    plan = Plan.objects.get(id=pk)    

    if plan.archived or \
    (request.user.username == 'Pasante' and not plan.new_p) or \
    (not request.user.has_perm('home.delete_plan') and plan.pc != '00000000') or \
    (plan.reviewer and not request.user.has_perm('home.sign_plan')):
        return render(request, 'errors/403.html', status=403)
    
    plan.archived = True
    plan.deleted_reason = request.POST.get('deleted_reason')
    plan.deleted_by = request.user.username
    plan.delete_time = timezone.now()

    plan.save()

    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    
    return redirect(reverse('plans') + '?header=deleted')
    
@login_required(login_url='/login/')
@permission_required('home.delete_archive_plan', raise_exception=True)
def deleteTruePlan(request, pk):

    item = Plan.objects.get(id = pk)

    if item.archived == True or request.user.is_superuser:
        item.delete()
        return redirect('plans')
    else:
        return render(request, 'errors/403.html', status=403)

@login_required(login_url='/login/')
@permission_required('home.delete_archive_plan', raise_exception=True)
@transaction.atomic
def deleteTruePlanMass(request):

    load = Plan.objects.filter(archived = True)

    for item in load:
        item.delete()
    print('Papelera de Planes de Calidad Vaciada')

    return redirect('plans-deleted')
    
    
@login_required(login_url='/login/')
@permission_required('home.delete_archive_plan', raise_exception=True)
def reincorporatePlan(request, pk):

    plan = Plan.objects.get(id=pk) 

    plan.disincorporated = False
    plan.disicomop_by = None
    plan.disicomop_reason = None
    plan.disicomop_time = None
    plan.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    if plan.pc == '00000000':
        return redirect(reverse('plans') + '?header=plans-0')
    return redirect('plans')
    
@login_required(login_url='/login/')
@permission_required('home.delete_archive_plan', raise_exception=True)
def restorePlan(request, pk):

    plan = Plan.objects.get(id=pk) 

    plan.archived = False
    plan.deleted_reason = None
    plan.deleted_by = None
    plan.delete_time = None
    plan.save()
    
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    if plan.pc == '00000000':
        return redirect(reverse('plans') + '?header=plans-0')
    return redirect('plans')

#--------------------------------------------------------------------->

#Material Model crud------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('home.add_materialtype', raise_exception=True)
def ajaxMaterialsAdd(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.id = get_id(Material)
            mat.save()
            return JsonResponse({'status':'success', 'message': 'Tipo de Material añadido exitosanente'})
        else:
            return JsonResponse({'status':'fail', 'message': form.errors.as_json()})
    else:
        return JsonResponse({'status':'fail', 'message': 'Error adding material type'})
    
@login_required(login_url='/login/')
@permission_required('home.add_material', raise_exception=True)
def addMaterial(request):

    form = MaterialForm()
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.id = get_id(Material)
            mat.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/materials/')

    context ={
        'form':form,
        'segment':'material',
        'back':True
        }
    return render(request, 'home/material_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.change_material', raise_exception=True)
def editMaterial(request, pk):

    material = Material.objects.get(id = pk)
    form = MaterialForm(instance = material)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance = material)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/materials/')

    context = {
        'form':form,
        'segment':'material',
        'back':True
        }

    return render(request, 'home/material_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.delete_material', raise_exception=True)#type:ignore
def deleteMaterial(request, pk):
    material = Material.objects.get(id = pk)    
    if request.method == 'POST':
        material.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('/materials/')

#--------------------------------------------------------------------->

#MaterialType Model crud---------------------------------------------->
@login_required(login_url='/login/')
@permission_required('home.add_materialtype', raise_exception=True)
def ajaxMaterialTypesAdd(request):
    if request.method == 'POST':
        form = MaterialTypeForm(request.POST)
        if form.is_valid():
            mat_t = form.save(commit=False)
            mat_t.id = get_id(MaterialType)
            mat_t.save()
            return JsonResponse({'status':'success', 'message': 'Material type added successfully'})
        else:
            return JsonResponse({'status':'fail', 'message': form.errors.as_json()})
    else:
        return JsonResponse({'status':'fail', 'message': 'Error adding material type'})
    
@login_required(login_url='/login/')
@permission_required('home.add_materialtype', raise_exception=True)
def addMaterialType(request):

    form = MaterialTypeForm()
    if request.method == 'POST':
        form = MaterialTypeForm(request.POST)
        if form.is_valid():
            mat_t = form.save(commit=False)
            mat_t.id = get_id(MaterialType)
            mat_t.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            else:    
                return redirect('/materials/types')
            
    context = {
        'form':form,
        'segment':'material',
        'back':True
        }                

    return render(request, 'home/material_type_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.change_materialtype', raise_exception=True)
def editMaterialType(request, pk):
    
    mat_type = MaterialType.objects.get(pk = pk)
    form = MaterialTypeForm(instance = mat_type)

    if request.method == 'POST':        
        form = MaterialTypeForm(request.POST, instance = mat_type)
        if form.is_valid():
            form.save()
            
            return redirect('/materials/types')

    context = {
        'form':form,
        'segment':'material',
        'back':True
        }
    
    return render(request, 'home/material_type_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.delete_materialtype', raise_exception=True)#type:ignore
def deleteMaterialType(request, pk):

    item = MaterialType.objects.get(pk = pk)
    if request.method == 'POST':  
        item.delete()
        
        return redirect('/materials/types')
    raise Http404

#--------------------------------------------------------------------->

#Essay Model crud------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('home.add_essay', raise_exception=True)
def addEssay(request):

    form = EssayForm()
    if request.method == 'POST':
        form = EssayForm(request.POST)
        if form.is_valid():
            essay = form.save(commit=False)
            essay.id = get_id(Essay)
            essay.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/essays/')

    context = {
        'form':form,
        'segment':'essay',
        'back':True
        }

    return render(request, 'home/essay_forms.html', context)
    
@login_required(login_url='/login/')
@permission_required('home.change_essay', raise_exception=True)
def editEssay(request, pk):

    essay = Essay.objects.get(id = pk)
    form = EssayForm(instance = essay)
    if request.method == 'POST':
        form = EssayForm(request.POST, instance = essay)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/essays/')

    context = {
        'form':form,
        'segment':'essay',
        'back':True
        }

    return render(request, 'home/essay_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.delete_essay', raise_exception=True)#type:ignore
def deleteEssay(request, pk):

    item = Essay.objects.get(id = pk)
    if request.method == 'POST':
        item.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('/essays/')

#--------------------------------------------------------------------->

#Unit Model crud------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('home.add_unit', raise_exception=True)
def addUnit(request):

    form = UnitForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            unit = form.save(commit=False)
            unit.id = get_id(Unit)
            unit.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            else:
                return redirect('/essays/units/')
    
    context = {
        'form':form,
        'segment':'essay',
        'back':True
        }

    return render(request, 'home/unit_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.change_unit', raise_exception=True)
def editUnit(request, pk):
    
    unit = Unit.objects.get(pk = pk)
    form = UnitForm(instance = unit)

    if request.method == 'POST':        
        form = UnitForm(request.POST, instance = unit)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/essays/units/')
    
    context = {
        'form':form,
        'segment':'essay',
        'back':True
        }

    return render(request, 'home/unit_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.delete_unit', raise_exception=True)#type:ignore
def deleteUnit(request, pk):

    item = Unit.objects.get(pk = pk)
    if request.method == 'POST':
        item.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('/essays/units/')

#--------------------------------------------------------------------->

#Client Model crud---------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('home.add_client', raise_exception=True)
@transaction.atomic
def addClient(request):

    form = ClientForm(request.POST or None)
    formset = DeliveryAddressFormset(request.POST or None, prefix='adresses')
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():

            client = form.save(commit=False)
            client.id = get_id(Client)
            client.save()

            addresses = formset.save(commit=False)
            for addrs in addresses:
                addrs.client = client
                
                addrs.save()

            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/clients/')

    context = {
        'form':form,
        'formset':formset,
        'segment':'client',
        'available_client':available_client(request.POST.get('rif_type') or None),
        'back':True
        }
    
    return render(request, 'home/client_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.change_client', raise_exception=True)
@transaction.atomic
def editClient(request, pk):

    client = Client.objects.get(pk = pk)
    form = ClientForm(request.POST or None, instance = client)
    formset = DeliveryAddressFormset(request.POST or None, prefix='adresses', instance = client)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():

            client = form.save()
            addresses = formset.save(commit=False)

            for rms in formset.deleted_objects:
                rms.delete()

            for addrs in addresses:
                if not addrs.client:
                    addrs.client = client
                
                addrs.save()

            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/clients/')
        
    context = {
        'form':form,
        'formset':formset,
        'segment':'client',
        'available_client':available_client(request.POST.get('rif_type') or None),
        'back':True
        }
    
    return render(request, 'home/client_forms.html', context)

def available_client(rt):
    try:
        last_client = Client.objects.filter(rif_type=rt).order_by('-rif_num')[0]
        a, b = last_client.rif_num.split('-')#type:ignore
        if int(b)+1 > 9:
            c, d = int(a)+1,0
        else:
            c, d = int(a), int(b)+1
        return f', siguiente disponible {rt}-{c:08}-{d}'
    except:
        return None

@login_required(login_url='/login/')
@permission_required('home.delete_client', raise_exception=True)#type:ignore
def deleteClient(request, pk):

    client = Client.objects.get(pk = pk)
    
    if request.method == 'POST':
        client.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('/clients/')

#--------------------------------------------------------------------->

#Provider Model crud-------------------------------------------------->
@login_required(login_url='/login/')
@permission_required('home.add_provider', raise_exception=True)
def addProvider(request):

    form = ProviderForm()
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            prov = form.save(commit=False)
            prov.id = get_id(Provider)
            prov.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/providers/')
    
    context = {
        'form':form,
        'segment':'provider',
        'back':True
        }
    
    return render(request, 'home/provider_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.change_provider', raise_exception=True)
def editProvider(request, pk):

    provider = Provider.objects.get(pk = pk)
    form = ProviderForm(instance = provider)
    if request.method == 'POST':
        form = ProviderForm(request.POST, instance = provider)
        if form.is_valid():
            form.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/providers/')
    
    context = {
        'form':form,
        'segment':'provider',
        'back':True
        }
    
    return render(request, 'home/provider_forms.html', context)

@login_required(login_url='/login/')
@permission_required('home.delete_provider', raise_exception=True)#type:ignore
def deleteProvider(request, pk):

    provider = Provider.objects.get(pk = pk)

    if request.method == 'POST':
        provider.delete()
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
    return redirect('/providers/')

#PDF------------------------------------------------------------------>
@login_required(login_url='/login/')
@permission_required('home.view_plan', raise_exception=True)
def pdfPlan(request, pk):

    plan_details = Plan.objects.get(id=pk)
    structure_list = Structure.objects.filter(plan__pk=pk)
    test_list = Test.objects.filter(plan__pk=pk)
    
    ink = []
    ink_c = 0
    adh = []
    adh_c = 0
    res = []
    res_c = 0
    sil = []
    sil_c = 0
    lac = []
    lac_c = 0
    par = []
    par_c = 0
    bar = []
    bar_c = 0
    pri = []
    pri_c = 0
    cer = []
    cer_c = 0
    com = []
    com_c = 0
    
    for n in structure_list:
        
        if n.material_type.name.startswith('Tintas'): #type:ignore
            ink.append(n.weight)
            ink_c+=1

        if n.material_type.name.startswith('Adhesivo'): #type:ignore
            adh.append(n.weight)
            adh_c+=1
        
        if n.material_type.name.startswith('Resina'): #type:ignore
            res.append(n.weight)
            res_c+=1
        
        if n.material_type.name.startswith('Silicona'): #type:ignore
            sil.append(n.weight)
            sil_c+=1

        if n.material_type.name.startswith('Laca'): #type:ignore
            lac.append(n.weight)
            lac_c+=1

        if n.material_type.name.startswith('Parafina'): #type:ignore
            par.append(n.weight)
            par_c+=1
            
        if n.material_type.name.startswith('Barniz'): #type:ignore
            bar.append(n.weight)
            bar_c+=1

        if n.material_type.name.startswith('Primer'): #type:ignore
            pri.append(n.weight)
            pri_c+=1
            
        if n.material_type.name.startswith('Cera'): #type:ignore
            cer.append(n.weight)
            cer_c+=1

        if n.material_type.name.startswith('Compuesto'): #type:ignore
            com.append(n.weight)
            com_c+=1

    context={
    'segment': 'plans',
    'plan_details':plan_details,
    'structure_list':structure_list,
    'test_list':test_list,    
    'ink': ink,
    'ink_c': ink_c,
    'adh': adh,
    'adh_c': adh_c,
    'res': res,
    'res_c': res_c,
    'par': par,
    'par_c': par_c,
    'sil': sil,
    'sil_c': sil_c,
    'lac': lac,
    'lac_c': lac_c,
    'bar': bar,
    'bar_c': bar_c,
    'pri': pri,
    'pri_c': pri_c,
    'cer': cer,
    'cer_c': cer_c,
    'com': com,
    'com_c': com_c,
    }    
    
    template = loader.get_template('home/plan_pdf.html')
    return HttpResponse(template.render(context, request))     
#--------------------------------------------------------------------->