from django.urls import path
from .views import *


urlpatterns = [
    path('<str:pk>/delete/', deleteDocument, name='delete_document'),
]