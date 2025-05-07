from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *

@admin.register(PrePrint)
class PrePrintAdmin(SimpleHistoryAdmin):
    pass
@admin.register(PdfRejects)
class PdfRejectsAdmin(SimpleHistoryAdmin):
    pass
@admin.register(PCRejects)
class PCRejectsAdmin(SimpleHistoryAdmin):
    pass