from django.urls import path
from .views import *

urlpatterns = [
    path("asset-list/", LoanListView.as_view(), name="asset-list"),
    path("disbursement-detail/", LoanDisbursementScheduleDetail.as_view(), name="disbursement-list"),
    path("budget-detail/",BudgetDetail.as_view(), name="budget-detail"),
    path("update-disbursement-status/",UpdateDisbursementStatus.as_view(),name="update-disbursement-status"),
    path("disbursement-status-mapping/",ReturnDisbursementStatusMapping.as_view(),name="disbursement-status-mapping"),
    path("dashboard-graph/",DashboardGraph.as_view(),name="dashboard-graph"),
    path("budget-master/",Budget.as_view(),name='budget-master'),
    path('budget-master/<int:id>/', Budget.as_view(), name='update-budget-master'),
    path("budget-summary/", BudgetSummary.as_view(),name='budget-summary'),
    path("project-list/", ProjectList.as_view(),name='project-list'),
    path("project/", ProjectCreateUpdateDelete.as_view(),name='project'),
    path("project/<int:id>", ProjectCreateUpdateDelete.as_view(),name='update-delete-project'),
    path("loan/", CreateRetrieveUpdateLoan.as_view(),name='loan'),
    path("loan/<int:loanid>",CreateRetrieveUpdateLoan.as_view(),name='delete-loan')
]
