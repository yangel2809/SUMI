# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - present Daniel Escalona
"""

from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    #path('register/', register_user, name="register"),
    
    path("logout/", LogoutView.as_view(), name="logout")
]
