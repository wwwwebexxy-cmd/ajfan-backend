from django.urls import path

from .views import CustomerListCreateView


app_name = "customers"

urlpatterns = [
    path("", CustomerListCreateView.as_view(), name="customer-list-create"),
]
