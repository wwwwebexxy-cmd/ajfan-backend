from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser

from .models import GovernmentInvoice
from .serializers import GovernmentInvoiceSerializer, GovernmentStaffSerializer


User = get_user_model()


class AdminOnlyMixin:
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)


class GovernmentStaffListView(AdminOnlyMixin, generics.ListAPIView):
    queryset = User.objects.filter(is_staff=True, is_active=True).order_by("email")
    serializer_class = GovernmentStaffSerializer


class GovernmentInvoiceListCreateView(AdminOnlyMixin, generics.ListCreateAPIView):
    serializer_class = GovernmentInvoiceSerializer

    def get_queryset(self):
        queryset = (
            GovernmentInvoice.objects.filter(is_deleted=False)
            .select_related("customer", "staff")
            .prefetch_related("items__service")
        )
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(customer__name__icontains=search)
                | Q(customer__email__icontains=search)
            )
        return queryset


class GovernmentInvoiceDetailView(AdminOnlyMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        GovernmentInvoice.objects.filter(is_deleted=False)
        .select_related("customer", "staff")
        .prefetch_related("items__service")
    )
    serializer_class = GovernmentInvoiceSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()
