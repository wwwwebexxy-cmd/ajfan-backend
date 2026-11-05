from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from .models import InvoiceNumberReservation, InvoiceNumberSequence, SalesInvoice
from .serializers import SalesInvoiceSerializer, StaffSerializer


User = get_user_model()


class AdminOnlyMixin:
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)


class StaffListView(AdminOnlyMixin, generics.ListAPIView):
    queryset = User.objects.filter(is_staff=True, is_active=True).order_by("email")
    serializer_class = StaffSerializer


class GenerateInvoiceNumberView(AdminOnlyMixin, APIView):
    @transaction.atomic
    def post(self, request):
        sequence = InvoiceNumberSequence.objects.select_for_update().get(pk=1)
        number = max(1, sequence.next_number)
        sequence.next_number = number + 1
        sequence.save(update_fields=("next_number",))
        reservation = InvoiceNumberReservation.objects.create(
            number=number,
            reserved_by=request.user,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        return Response(
            {
                "invoice_number": f"{number:03d}",
                "reservation_token": str(reservation.token),
            },
            status=status.HTTP_201_CREATED,
        )


class SalesInvoiceListCreateView(AdminOnlyMixin, generics.ListCreateAPIView):
    serializer_class = SalesInvoiceSerializer

    def get_queryset(self):
        queryset = (
            SalesInvoice.objects.filter(is_deleted=False)
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


class SalesInvoiceDetailView(AdminOnlyMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        SalesInvoice.objects.filter(is_deleted=False)
        .select_related("customer", "staff")
        .prefetch_related("items__service")
    )
    serializer_class = SalesInvoiceSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()
