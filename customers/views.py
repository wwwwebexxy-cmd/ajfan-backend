from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser

from .models import Customer
from .serializers import CustomerCreateSerializer, CustomerDetailSerializer, CustomerListSerializer


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.filter(is_deleted=False)
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CustomerListSerializer
        return CustomerCreateSerializer


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.filter(is_deleted=False)
    serializer_class = CustomerDetailSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def perform_destroy(self, instance):
        instance.soft_delete()
