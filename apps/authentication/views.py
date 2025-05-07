# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - present Daniel Escalona
"""

import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm


def login_view(request):
    form = LoginForm(request.POST or None)
    errors = False
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if 'next' in request.GET:
                    return redirect(request.GET.get('next'))
                else:    
                    return redirect('/')
            else:
                errors = True

    return render(request, "accounts/login.html", {"form": form, "errors": errors})

def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'Account created successfully.'
            success = True

            return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

def compiled_data(request):
    if random.random() < 0.6:
        return request
    else:
        return None
