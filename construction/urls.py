from django.urls import path
from .views import *

urlpatterns = [
    path("asset-list/", LoanListView.as_view(), name="asset-list"),
    path("disbursement-detail/", LoanDisbursementScheduleDetail.as_view(), name="disbursement-list"),
    path("budget-detail/",BudgetDetail.as_view(), name="budget-detail"),
    path("update-disbursement-status/",UpdateDisbursementStatus.as_view(),name="update-disbursement-status"),
    path("status-mapping/",ReturnStatusMapping.as_view(),name="status-mapping"),
    path("dashboard-graph/",DashboardGraph.as_view(),name="dashboard-graph"),
    path("budget-master/",Budget.as_view(),name='budget-master'),
    path('budget-master/<int:id>/', Budget.as_view(), name='update-budget-master'),
    path("budget-summary/", BudgetSummary.as_view(),name='budget-summary'),
    path("project-list/", ProjectList.as_view(),name='project-list'),
    path("project/", ProjectCreateUpdateDelete.as_view(),name='project'),
    path("project/<int:id>", ProjectCreateUpdateDelete.as_view(),name='update-delete-project'),
    path("loan/", CreateRetrieveUpdateLoan.as_view(),name='loan'),
    path("loan/<int:loanid>",CreateRetrieveUpdateLoan.as_view(),name='delete-loan'),
    path("uses-list/",UsesListView.as_view(), name = 'uses-list'),
    path("insert-uses/",InsertUsesforBudgetMaster.as_view(), name='insert-uses'),
    path("list-uses-type/",ListUsesType.as_view(),name='list-uses-type'),
    path("loan-approval/",LoanApprovalStatus.as_view(),name="loan-approval"),
    path("submit-budget/",LoanApprovalStatus.as_view(),name="submit-budget/"),
    path("draw-request/",CreateUpdateDrawRequest.as_view(),name='draw-request')
]
