from django.urls import path
from .views import UserProjectsView

urlpatterns = [
    path('user-projects/', UserProjectsView.as_view(), name='user-projects'),
]