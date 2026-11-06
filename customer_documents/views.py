from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser

from .models import CustomerDocument
from .serializers import CustomerDocumentSerializer


class AdminOnlyMixin:
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)


class CustomerDocumentListCreateView(AdminOnlyMixin, generics.ListCreateAPIView):
    serializer_class = CustomerDocumentSerializer

    def get_queryset(self):
        queryset = CustomerDocument.objects.filter(is_deleted=False).select_related("customer")
        expiry_from = parse_date(self.request.query_params.get("expiry_from", ""))
        expiry_to = parse_date(self.request.query_params.get("expiry_to", ""))
        customer = self.request.query_params.get("customer", "").strip()
        if expiry_from:
            queryset = queryset.filter(expiry_date__gte=expiry_from)
        if expiry_to:
            queryset = queryset.filter(expiry_date__lte=expiry_to)
        if customer.isdigit():
            queryset = queryset.filter(customer_id=int(customer))
        return queryset


class CustomerDocumentDetailView(AdminOnlyMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerDocument.objects.filter(is_deleted=False).select_related("customer")
    serializer_class = CustomerDocumentSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()
