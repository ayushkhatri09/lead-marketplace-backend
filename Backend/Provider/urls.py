# from django.urls import path

# from .views import NearbyProviderAPIView, ProviderGoogleCallbackAPIView, ProviderGoogleExchangeAPIView, ProviderGoogleLoginAPIView, ProviderRegisterAPIView,ProviderLoginAPIView, ProviderProfileAPIView,ProviderTokenRefreshAPIView, ToggleProviderActiveAPIView


# urlpatterns = [

#     path(
#         "register/",
#         ProviderRegisterAPIView.as_view(),
#         name="provider-register"
#     ),

#     path(
#         "login/",
#         ProviderLoginAPIView.as_view(),
#         name="provider-login"
#     ),

#     path(
#         "profile/",
#         ProviderProfileAPIView.as_view(),
#         name="provider-profile"
#     ),

#     path(
#     "token/refresh/",
#     ProviderTokenRefreshAPIView.as_view(),
#     name="provider-token-refresh",
# ),

# path(
#     "nearby/",
#     NearbyProviderAPIView.as_view(),
#     name="nearby-providers"
# ),

#  path(
#         "toggle-active/",
#         ToggleProviderActiveAPIView.as_view(),
#         name="provider-toggle-active"
#     ),

# path(
#     "google/login/",
#     ProviderGoogleLoginAPIView.as_view(),
# ),


# path(
#     "google/callback/",
#     ProviderGoogleCallbackAPIView.as_view(),
# ),

# path("google/exchange/", ProviderGoogleExchangeAPIView.as_view(), name="provider-google-exchange"),

     

# ]

from django.urls import path

from .views import (
    NearbyProviderAPIView,
    ProviderGoogleCallbackAPIView,
    ProviderGoogleExchangeAPIView,
    ProviderGoogleLoginAPIView,
    ProviderOnboardingAPIView,
    ProviderRegisterAPIView,
    ProviderLoginAPIView,
    ProviderProfileAPIView,
    ProviderTokenRefreshAPIView,
    ToggleProviderActiveAPIView,
)


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

path(
    "google/login/",
    ProviderGoogleLoginAPIView.as_view(),
),


path(
    "google/callback/",
    ProviderGoogleCallbackAPIView.as_view(),
),

path("google/exchange/", ProviderGoogleExchangeAPIView.as_view(), name="provider-google-exchange"),

path(
    "onboarding/",ProviderOnboardingAPIView.as_view(),name="provider-onboarding")

]