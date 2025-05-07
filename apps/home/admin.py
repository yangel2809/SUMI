"""
Copyright (c) 2022 - present, Daniel Escalona
"""
from django.contrib import admin
from django import forms
from django.contrib.admin.options import TabularInline
from django.template.loader import get_template
from simple_history.admin import SimpleHistoryAdmin
from simple_history.models import HistoricalRecords
from .models import *

def get_related_historical_records(historical_plan):
    # Accessing historical structures related to the historical plan
    historical_structures = HistoricalStructure.objects.filter(plan_id=historical_plan.instance.id)#type:ignore
    
    # Accessing historical tests related to the historical plan
    historical_tests = HistoricalTest.objects.filter(plan_id=historical_plan.instance.id)#type:ignore
    
    return historical_structures, historical_tests

class StructureInlineAdmin(admin.TabularInline):
    model = Structure

class TestInlineAdmin(admin.TabularInline):
    model = Test

class PlanAdmin(SimpleHistoryAdmin):
    change_form_template = 'admin/historical_change_form.html'
    inlines = [StructureInlineAdmin, TestInlineAdmin]
    list_display = ('product', 'client', 'pc', 'revission', 'gp_code', 'id', 'archived')
    history_list_display = ["status"]
    fields = (
            'pc',
            'revission',
            'rev_date',
            'client',
            'product',
            'gp_code',
            'code',
            #'format',
            'structure_inline',
            'test_inline',
            'observation',
            'continuation',
            'dispatch_conditions',
            'elaborator',
            'reviewer',         
            'date_created',
            ('archived', 'deleted_by', 'delete_time'),
            ('disincorporated', 'disicomop_by', 'disicomop_time')
        )
    
    readonly_fields = ('structure_inline', 'test_inline','date_created', 'archived', 'deleted_by', 'delete_time', 'disincorporated', 'disicomop_by', 'disicomop_time' ) # method as readonly field , 'test_inline'

    def structure_inline(self, *args, **kwargs):
        context = getattr(self.response, 'context_data', None) or {}
        inline = None  # Initialize inline to None
        if context.get('inline_admin_formsets'):
            inline = context['inline_admin_formset'] = context['inline_admin_formsets'].pop(0)
            return get_template(inline.opts.template).render(context, self.request)
        else:
            # Handle the case where inline is not available
            return "No inline formsets available"

    
    def test_inline(self, *args, **kwargs):
        context = getattr(self.response, 'context_data', None) or {}
        inline = None  # Initialize inline to None
        if context.get('inline_admin_formsets'):
            inline = context['inline_admin_formset'] = context['inline_admin_formsets'].pop(0)
            return get_template(inline.opts.template).render(context, self.request)
        else:
            # Handle the case where inline is not available
            return "No inline formsets available"

    def render_change_form(self, request, *args, **kwargs):
        self.request = request
        self.response = super().render_change_form(request, *args, **kwargs)
        return self.response
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        plan_instance = self.model.objects.get(pk=object_id)
        
        # Retrieve the historical record for the plan instance
        historical_plan = plan_instance.history.latest()

        # Retrieve the historical records for the related Structure and Test objects
        # by filtering the historical models directly
        historical_structures = Structure.history.filter(plan_id=historical_plan.instance.id)
        historical_tests = Test.history.filter(plan_id=historical_plan.instance.id)
        
        # Add the historical records to the extra_context
        extra_context['historical_structures'] = historical_structures
        extra_context['historical_tests'] = historical_tests
        
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )
    
    def history_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        plan_instance = self.model.objects.get(pk=object_id)
        
        # Get the historical record for the selected version
        version_id = request.GET.get('version_id')
        if version_id:
            historical_plan = plan_instance.history.get(history_id=version_id)
            
            # Fetch the historical versions of Structure and Test related to this version of the Plan
            historical_structures = Structure.history.filter(history_date__lte=historical_plan.history_date, plan_id=plan_instance.id)
            historical_tests = Test.history.filter(history_date__lte=historical_plan.history_date, plan_id=plan_instance.id)
            
            # Add the historical records to the extra_context
            extra_context['historical_structures'] = historical_structures
            extra_context['historical_tests'] = historical_tests
        
        return super().history_view(request, object_id, extra_context=extra_context)


class ClientAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'rif_type', 'rif_num')
    history_list_display = ["status"]

class ProviderAdmin(SimpleHistoryAdmin):
    list_display = ('name',)
    history_list_display = ["status"]

""" class FormatAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'revission', 'rev_date')
    history_list_display = ["status"] """

class MaterialAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'provider', 'material_type')
    history_list_display = ["status"]

class StructureAdmin(SimpleHistoryAdmin):
    list_display = ('plan', 'material_type', 'weight', 'thickness')
    history_list_display = ["status"]

class EssayAdmin(SimpleHistoryAdmin):
    ordering = ('method',)
    list_display = ('name', 'detail', 'method', 'priority', 'unit')
    history_list_display = ["status"]

class UnitAdmin(SimpleHistoryAdmin):
    ordering = ('id',)
    list_display = ('id', 'name', 'symbol', 'description')
    history_list_display = ["status"]

class TestAdmin(SimpleHistoryAdmin):
    list_display = ('plan', 'essay', 'critic', 'spec')   
    history_list_display = ["status"]

@admin.register(DeincorporateRequest)
class DeincorporateRequestAdmin(admin.ModelAdmin):
    pass

admin.site.register(Client, ClientAdmin)
#admin.site.register(Format, FormatAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(MaterialType)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(Essay, EssayAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Test, TestAdmin)

