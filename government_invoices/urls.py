from django.urls import path

from .views import (
    GovernmentInvoiceDetailView,
    GovernmentInvoiceListCreateView,
    GovernmentStaffListView,
)


app_name = "government-invoices"

urlpatterns = [
    path("staff/", GovernmentStaffListView.as_view(), name="staff-list"),
    path("", GovernmentInvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("<int:pk>/", GovernmentInvoiceDetailView.as_view(), name="invoice-detail"),
]
