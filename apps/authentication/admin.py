# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - present Daniel Escalona
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *
from django.contrib.auth.models import Permission

@admin.register(Permission)
class PermissionAdmin(SimpleHistoryAdmin):
    list_display = ('codename', 'name',  'content_type')#'test_material', 'test_material_check',
    history_list_display = ["status"]
    
# Register your models here.
#@admin.register(UserRole)
#class UserRoleAdmin(SimpleHistoryAdmin):
#    pass