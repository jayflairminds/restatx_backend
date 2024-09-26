from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    path("api/", include("users.urls")),
    path("api/", include("construction.urls")),
    path("api/", include("doc_summary_qna.urls")),
    path("api/", include("document_management.urls")),
    path("api/", include("alerts.urls")),
    path("payments/",include("user_payments.urls"))
]
