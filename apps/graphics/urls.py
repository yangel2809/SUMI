from django.urls import path, re_path
from .views import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('update_pre_print_status/', update_pre_print_status, name='update_pp_status'),
    path('send_email/', test_email, name='send_email'),

]