# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView

# from .views import GoogleCallbackAPIView, GoogleLoginAPIView, UserRegisterAPIView, UserLoginAPIView,UserProfileAPIView,UserLogoutAPIView



# urlpatterns = [

#     path(
#         "register/",
#         UserRegisterAPIView.as_view(),
#         name="user-register"
#     ),

#     path(
#         "login/",
#         UserLoginAPIView.as_view()
#     ),

#     path(
#         "profile/",
#         UserProfileAPIView.as_view()
#     ),

#     path(
#         "token/refresh/", 
#         TokenRefreshView.as_view()),

#      path(
#         "logout/",
#         UserLogoutAPIView.as_view(),
#         name="user-logout"
#     ),

#         path(
#         "google/login/",
#         GoogleLoginAPIView.as_view(),
#         name="google-login"
# ),

#     path(
#         "google/callback/",
#         GoogleCallbackAPIView.as_view(),
#         name="google-callback"
# ),    

    

# ]

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    GoogleCallbackAPIView,
    GoogleLoginAPIView,
    UserGoogleExchangeAPIView,
    UserRegisterAPIView,
    UserLoginAPIView,
    UserProfileAPIView,
    UserLogoutAPIView,
    UserOnboardingAPIView,
)


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
        TokenRefreshView.as_view()
    ),

    path(
        "logout/",
        UserLogoutAPIView.as_view(),
        name="user-logout"
    ),

    path(
        "google/login/",
        GoogleLoginAPIView.as_view(),
        name="google-login"
    ),

    path(
        "google/callback/",
        GoogleCallbackAPIView.as_view(),
        name="google-callback"
    ),

    path(
        "google/exchange/",
        UserGoogleExchangeAPIView.as_view(),
        name="google-exchange"
    ),

    path(
        "onboarding/",
        UserOnboardingAPIView.as_view(),
        name="user-onboarding"
    ),

]