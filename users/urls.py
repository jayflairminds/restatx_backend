from django.urls import path
from knox import views as knox_views
from django.urls import path
from .views import *

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("user/", GetUserView.as_view(), name="get_user"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("list-users/",UserList.as_view(),name="list-user-on-roletype")
]
