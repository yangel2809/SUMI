from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.template.loader import get_template
from .models import *

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin): 
    list_display = ('label', 'file')
