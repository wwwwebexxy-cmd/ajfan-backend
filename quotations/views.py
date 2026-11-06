from django.db.models import Q
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser

from .models import Quotation
from .serializers import QuotationSerializer


class AdminOnlyMixin:
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)


class QuotationListCreateView(AdminOnlyMixin, generics.ListCreateAPIView):
    serializer_class = QuotationSerializer

    def get_queryset(self):
        queryset = (
            Quotation.objects.filter(is_deleted=False)
            .select_related("customer")
            .prefetch_related("items__service")
        )
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(customer__name__icontains=search)
                | Q(customer__email__icontains=search)
            )
        return queryset


class QuotationDetailView(AdminOnlyMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Quotation.objects.filter(is_deleted=False)
        .select_related("customer")
        .prefetch_related("items__service")
    )
    serializer_class = QuotationSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()
