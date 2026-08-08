from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegisterAPIView, UserLoginAPIView,UserProfileAPIView,UserLogoutAPIView



urlpatterns = [

    path(
        "register/",
        UserRegisterAPIView.as_view(),
        name="user-register"
    ),

    path(
        "login/",
        UserLoginAPIView.as_view()
    ),

    path(
        "profile/",
        UserProfileAPIView.as_view()
    ),

    path(
        "token/refresh/", 
        TokenRefreshView.as_view()),

     path(
        "logout/",
        UserLogoutAPIView.as_view(),
        name="user-logout"
    ),    

    

]