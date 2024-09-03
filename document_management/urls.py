from django.urls import path
from .views import *

urlpatterns = [
    path("document-management/",DocumentManagement.as_view(), name='document-management'),
    path("list-of-documents/",ListOfDocument.as_view(),name="list-of-documents"),
    path("delete-document/<int:id>",DocumentManagement.as_view(),name="list-of-documents"),
    path("summary-document/",DocSummaryView.as_view(),name="summary-document"),
    path("document-update-status/",DocumentStatus.as_view(),name="document-update-status"),
    path("documenttype/",CreateRetrieveUpdateDocumentType.as_view(), name="documenttype"),
    path("documenttype/<int:id>",CreateRetrieveUpdateDocumentType.as_view(), name="documenttype"),
    path("documentdetail/",CreateRetrieveUpdateDocumentDetail.as_view(),name="documentdetail"),
    path("documenttypes-loan/",ListDocumentTypeForLoan.as_view(),name="documenttypes-loan")
]