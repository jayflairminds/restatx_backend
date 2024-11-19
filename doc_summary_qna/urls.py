from django.urls import path
from knox import views as knox_views
from django.urls import path
from doc_summary_qna.views import UploadView,ResponseView 
from .views import *

urlpatterns = [
    path("upload/", UploadView.as_view(), name="upload"),
    path("response/", ResponseView.as_view(), name="response"),
    path('extract/', ExtractText.as_view(), name='extract')  
]