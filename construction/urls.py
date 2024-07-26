from django.urls import path
from .views import *

urlpatterns = [
    path("asset-list/", LoanListView.as_view(), name="asset-list"),
    path("disbursement-detail/", LoanDisbursementScheduleDetail.as_view(), name="disbursement-list"),
    path("budget-detail/",BudgetDetail.as_view(), name="budget-detail"),
    path("update-disbursement-status/",UpdateDisbursementStatus.as_view(),name="update-disbursement-status"),
    path("disbursement-status-mapping/",ReturnDisbursementStatusMapping.as_view(),name="disbursement-status-mapping"),
    path("dashboard-graph/",DashboardGraph.as_view(),name="dashboard-graph"),
]
