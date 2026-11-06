from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser

from .models import Reminder
from .serializers import ReminderSerializer


class AdminOnlyMixin:
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication, SessionAuthentication)


class ReminderListCreateView(AdminOnlyMixin, generics.ListCreateAPIView):
    serializer_class = ReminderSerializer

    def get_queryset(self):
        queryset = Reminder.objects.filter(is_deleted=False).select_related("customer")
        due_from = parse_date(self.request.query_params.get("due_from", ""))
        due_to = parse_date(self.request.query_params.get("due_to", ""))
        customer = self.request.query_params.get("customer", "").strip()
        if due_from:
            queryset = queryset.filter(due_date__gte=due_from)
        if due_to:
            queryset = queryset.filter(due_date__lte=due_to)
        if customer.isdigit():
            queryset = queryset.filter(customer_id=int(customer))
        return queryset


class ReminderDetailView(AdminOnlyMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Reminder.objects.filter(is_deleted=False).select_related("customer")
    serializer_class = ReminderSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()
