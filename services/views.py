from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser

from .models import Service
from .serializers import ServiceSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.filter(is_deleted=False)
    serializer_class = ServiceSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.filter(is_deleted=False)
    serializer_class = ServiceSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def perform_destroy(self, instance):
        instance.soft_delete()
