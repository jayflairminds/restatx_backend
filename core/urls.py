from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("construction.urls")),
    path("api/", include("doc_summary_qna.urls"))
]
