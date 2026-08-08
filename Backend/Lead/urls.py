from django.urls import path
from .views import LeadCreateAPIView,MyLeadAPIView, ProviderHistoryAPIView, ProviderLeadListAPIView,AcceptLeadAPIView,PurchaseLeadAPIView


urlpatterns=[
    path('create/',LeadCreateAPIView.as_view(), name="lead-create"),
    path("my-leads/",MyLeadAPIView.as_view(),name="my-leads"),
     path("provider-leads/",ProviderLeadListAPIView.as_view(),name="provider-leads"),
    path(
    "accept/<int:lead_id>/",
    AcceptLeadAPIView.as_view(),
    name="accept-lead",
    ),
    path(
    "purchase/<int:lead_id>/",
    PurchaseLeadAPIView.as_view(),
    name="purchase-lead",
    ),
    path(
    "provider-history/",
    ProviderHistoryAPIView.as_view(),
    name="provider-history"
),
]
