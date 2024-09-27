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
    path("list-users/",UserList.as_view(),name="list-user-on-roletype"),
    path("change-password/",PasswordChange.as_view(),name="change-password"),
    path("delete-user/<int:id>",DeleteUser.as_view(),name="delete-user"),
    path("password-reset/", PasswordResetRequest.as_view(), name="password-reset"), # API to request password reset email
    path("password-confirm/<uidb64>/<token>/", PasswordResetConfirm.as_view(), name="password-confirm") # API to confirm password reset

]
