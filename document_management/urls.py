from django.urls import path
from .views import *

urlpatterns = [
    path("document-management/",DocumentManagement.as_view(), name='document-management'),
    path("list-of-documents/",ListOfDocument.as_view(),name="list-of-documents"),
    path("delete-document/<int:id>",DocumentManagement.as_view(),name="list-of-documents")
]