from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.template.loader import get_template
from .models import *

@admin.register(SaleOrder)
class SaleOrderAdmin(SimpleHistoryAdmin):
    pass
@admin.register(Representative)
class RepresentativeAdmin(SimpleHistoryAdmin):
    pass
@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(SimpleHistoryAdmin):
    pass
@admin.register(SaleOrderReview)
class SaleOrderReviewAdmin(SimpleHistoryAdmin):
    pass

class SalesStructureInlineAdmin(admin.TabularInline):
    model = SalesStructure
@admin.register(SalesTestRequest)
class SalesTestRequestAdmin(SimpleHistoryAdmin):
    inlines = [SalesStructureInlineAdmin]
    readonly_fields = ('essays_inline',)
    list_display=('client','product')
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