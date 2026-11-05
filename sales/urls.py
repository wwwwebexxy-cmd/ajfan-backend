from django.urls import path

from .views import (
    SalesInvoiceDetailView,
    SalesInvoiceListCreateView,
    GenerateInvoiceNumberView,
    StaffListView,
)


app_name = "sales"

urlpatterns = [
    path("generate-number/", GenerateInvoiceNumberView.as_view(), name="invoice-number-generate"),
    path("staff/", StaffListView.as_view(), name="staff-list"),
    path("", SalesInvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("<int:pk>/", SalesInvoiceDetailView.as_view(), name="invoice-detail"),
]
