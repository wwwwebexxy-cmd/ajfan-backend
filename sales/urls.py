from django.urls import path

from .views import (
    SalesInvoiceDetailView,
    SalesInvoiceListCreateView,
    StaffListView,
)


app_name = "sales"

urlpatterns = [
    path("staff/", StaffListView.as_view(), name="staff-list"),
    path("", SalesInvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("<int:pk>/", SalesInvoiceDetailView.as_view(), name="invoice-detail"),
]
