from django.urls import path
from .views import *

urlpatterns = [
    path("document-management/",DocumentManagement.as_view(), name='document-management')
]