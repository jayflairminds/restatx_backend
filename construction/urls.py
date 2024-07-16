from django.urls import path
from .views import LoanListView,LoanDisbursementScheduleDetail

urlpatterns = [
    path("asset-list/", LoanListView.as_view(), name="asset-list"),
    path("disbursement-detail/", LoanDisbursementScheduleDetail.as_view(), name="asset-list"),
]
