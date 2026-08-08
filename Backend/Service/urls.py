from  django.urls import path
from .views import ServiceListApiView

urlpatterns=[

    path('list/',ServiceListApiView.as_view(),name='service_list')
]