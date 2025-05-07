from django.contrib import admin
from django import forms
from django.contrib.admin.options import TabularInline
from django.template.loader import get_template
from simple_history.admin import SimpleHistoryAdmin
from .models import *

@admin.register(EntryElement)
class EntryElementAdmin(SimpleHistoryAdmin):
    pass
class TestStructureInlineAdmin(admin.TabularInline):
    model = TestStructure
@admin.register(TestRequest)
class TestRequestAdmin(SimpleHistoryAdmin):
    inlines = [TestStructureInlineAdmin]
    ordering = ['-number']
    list_display = ('number', 'product', 'client', 'date', 'pr')
    history_list_display = ["status"]
    fields = (
            ('number', 'company', 'origin', 'entry_element'),
            ('date', 'production_order'),
            #art
            ('art_number', 'art_date', 'product', 'design'),
            ('check_test_client', 'test_client', 'client'), 
            #_TestStructure
            'structure_inline',
            ('print_selector', 'printer', 'colors'),
            ('surface_selector', 'reverse_selector', 'sindex'),
            ('sustrate_width', 'print_width', 'print_width_unit'),
            #_Lamination
            #'lamination_selector',
            #'lamination_inline',
            #dimendiosns
            ('dist_boder_cell_material', 'repetition', 'repetition_unit', 'width_photo', 'lenght_photo', 'unit_photo', 'develop', 'develop_unit'),
            #bobbin
            ('check_bobbin', 'width_bobbin', 'width_bobbin_unit', 'exterior_dia_bobbin', 'exterior_dia_bobbin_unit', 'core_dia_bobbin'),
            #ream
            ('check_ream', 'width_ream', 'lenght_ream', 'weight_ream'),
            ('quantity', 'unit', 'tolerance', 'winding', 'winding_description'),
            ('packaging', 'tie_color'),
            'observation', 
            ('applicant', 'elaborator', 'reviewer'),
            ('pre_print', 'colorimetry', 'plan_crx', 'plan_mcl', 'logistics', 'quality'),
            ('archived', 'archived_time'),
            ('touched', 'deleted', 'deleted_time'),
            'deleted_reason'
            )
    
    readonly_fields = ('structure_inline',)

    def pr(self, obj):
        if obj.production_order:
            return f'PR-{obj.production_order}'
        return '-'
    
    def structure_inline(self, *args, **kwargs):
        context = getattr(self.response, 'context_data', None) or {}
        if context['inline_admin_formsets']:
            inline = context['inline_admin_formset'] = context['inline_admin_formsets'].pop(0)
            return get_template(inline.opts.template).render(context, self.request)#type:ignore
        else:
            return get_template(inline.opts.template).render(self.request)#type:ignore
    
    def render_change_form(self, request, *args, **kwargs):
        self.request = request
        self.response = super().render_change_form(request, *args, **kwargs)
        return self.response

@admin.register(TestStructure)
class TestStructureAdmin(SimpleHistoryAdmin):
    list_display = ('test_request', 'material_type',  'weight', 'thickness')#'test_material', 'test_material_check',
    history_list_display = ["status"]
    fields = (
            'test_material_check',
            'material_type',
            'test_material',
            'weight',
            'thickness'
        ),

@admin.register(Printer)
class PrinterAdmin(SimpleHistoryAdmin):
    list_display = ('name',)
    history_list_display = ["status"]
@admin.register(Laminator)
class LaminatorAdmin(SimpleHistoryAdmin):
    list_display = ('name',)
    history_list_display = ["status"]
@admin.register(QualityAnalyst)
class QualityAnalystAdmin(SimpleHistoryAdmin):
    pass
@admin.register(ProductionOperator)
class ProductionOperatorAdmin(SimpleHistoryAdmin):
    pass
@admin.register(Rewinder)
class RewinderAdmin(SimpleHistoryAdmin):
    pass
@admin.register(Cutter)
class CutterAdmin(SimpleHistoryAdmin):
    pass
@admin.register(Annex)
class AnnexAdmin(SimpleHistoryAdmin):
    pass
class LaminationEssayInlineAdmin(admin.TabularInline):
    model = LaminationEssay
@admin.register(LaminatorBoot)
class LaminatorBootAdmin(SimpleHistoryAdmin):
    inlines = [LaminationEssayInlineAdmin]
    readonly_fields = ('essays_inline',)
    list_display=('pr','name')
    def essays_inline(self, *args, **kwargs):
        context = getattr(self.response, 'context_data', None) or {}
        if context['inline_admin_formsets']:
            inline = context['inline_admin_formset'] = context['inline_admin_formsets'].pop(0)
            return get_template(inline.opts.template).render(context, self.request)#type:ignore
        else:
            return get_template(inline.opts.template).render(self.request)#type:ignore
        
    def pr(self, obj):
        return f'PR-{obj.test_request.production_order}'
    
    def name(self, obj):
        return f'LAM paso: {obj.step} - {obj.test_request.product}'

    def render_change_form(self, request, *args, **kwargs):
        self.request = request
        self.response = super().render_change_form(request, *args, **kwargs)
        return self.response
@admin.register(TechnicalSpecs)
class TechnicalSpecsAdmin(SimpleHistoryAdmin):
    pass
@admin.register(TestFile)
class TestFileAdmin(SimpleHistoryAdmin):
    pass
@admin.register(TestFileEssay)
class TestFileEssayAdmin(SimpleHistoryAdmin):
    list_display = ('test_file', 'essay')
    history_list_display = ["status"]
@admin.register(TestFileEssayResult)
class TestFileEssayResultAdmin(SimpleHistoryAdmin):
    pass
@admin.register(Bobbin)
class BobbinAdmin(SimpleHistoryAdmin):
    pass
@admin.register(PrinterBoot)
class PrinterBootAdmin(SimpleHistoryAdmin):
    pass

