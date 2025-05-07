# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - present Daniel Escalona
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.TextField(max_length=15, default='Personal', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.role}'#type:ignore