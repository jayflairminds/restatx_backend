from django.urls import path
from .views import LoanListView

urlpatterns = [
    path("asset-list/", LoanListView.as_view(), name="asset-list"),
]
