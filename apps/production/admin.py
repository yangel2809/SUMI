from django.contrib import admin
from django import forms
from django.contrib.admin.options import TabularInline
from django.template.loader import get_template
from simple_history.admin import SimpleHistoryAdmin

from apps.essays.models import Laminator
from .models import *

@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    pass
@admin.register(PrinterBoot)
class PrinterBootAdmin(SimpleHistoryAdmin):
    pass
class LaminationEssayInlineAdmin(admin.TabularInline):
    model = LaminationEssay
@admin.register(LaminatorBoot)
class LaminatorBootAdmin(SimpleHistoryAdmin):
    inlines = [LaminationEssayInlineAdmin]
    readonly_fields = ('essays_inline',)

    def essays_inline(self, *args, **kwargs):
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
    
@admin.register(CutterBoot)
class CutterBootAdmin(SimpleHistoryAdmin):
    pass
@admin.register(TechnicalSpecs)
class TechnicalSpecsAdmin(SimpleHistoryAdmin):
    pass

@admin.register(TestFile)
class TestFileAdmin(SimpleHistoryAdmin):
    pass

@admin.register(TestFileEssay)
class TestFileEssayAdmin(SimpleHistoryAdmin):
    pass

@admin.register(TestFileEssayResult)
class TestFileEssayResultAdmin(SimpleHistoryAdmin):
    pass

@admin.register(Bobbin)
class BobbinAdmin(SimpleHistoryAdmin):
    pass