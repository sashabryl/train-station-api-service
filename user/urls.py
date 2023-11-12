from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import CreateUserView, ManageUserView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("verify/", TokenVerifyView.as_view(), name="verify-token"),
    path("me/", ManageUserView.as_view(), name="me"),
]

app_name = "user"
