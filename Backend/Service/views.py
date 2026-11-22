# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny

# from .models import Service
# from .serializers import ServiceListSerializer


# class ServiceListApiView(APIView):
#      permission_classes=[AllowAny]
#      def get(self,request):
#           service=Service.objects.filter(
#                is_active=True
#           ).order_by('name')

#           serializer=ServiceListSerializer(
#                service,many=True
#           )

#           return Response(
#                {
#                     'message':"service list fetched succesfully",
#                     'count':service.count(),
#                     'data':serializer.data,

#                },
#                status=status.HTTP_200_OK
#           )


from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Service
from .serializers import ServiceListSerializer

SERVICE_LIST_CACHE_KEY = "service_list_v1"
SERVICE_LIST_TTL = 60 * 10  # 10 minute


class ServiceListApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payload = cache.get(SERVICE_LIST_CACHE_KEY)

        if payload is None:
            services = Service.objects.filter(
                is_active=True
            ).order_by("name")

            data = list(
                ServiceListSerializer(services, many=True).data
            )

            payload = {
                "message": "service list fetched succesfully",
                "count": len(data),
                "data": data,
            }

            cache.set(
                SERVICE_LIST_CACHE_KEY,
                payload,
                timeout=SERVICE_LIST_TTL,
            )

        return Response(payload, status=status.HTTP_200_OK)