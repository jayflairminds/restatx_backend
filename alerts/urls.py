from django.urls import path
from .views import *

urlpatterns = [
    path("notification/",NotificationManager.as_view(),name ="notification")
]