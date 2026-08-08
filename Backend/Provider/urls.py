from django.urls import path

from .views import NearbyProviderAPIView, ProviderRegisterAPIView,ProviderLoginAPIView, ProviderProfileAPIView,ProviderTokenRefreshAPIView, ToggleProviderActiveAPIView


urlpatterns = [

    path(
        "register/",
        ProviderRegisterAPIView.as_view(),
        name="provider-register"
    ),

    path(
        "login/",
        ProviderLoginAPIView.as_view(),
        name="provider-login"
    ),

    path(
        "profile/",
        ProviderProfileAPIView.as_view(),
        name="provider-profile"
    ),

    path(
    "token/refresh/",
    ProviderTokenRefreshAPIView.as_view(),
    name="provider-token-refresh",
),

path(
    "nearby/",
    NearbyProviderAPIView.as_view(),
    name="nearby-providers"
),

 path(
        "toggle-active/",
        ToggleProviderActiveAPIView.as_view(),
        name="provider-toggle-active"
    ),

     

]