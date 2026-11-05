from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import Customer
from services.models import Service

from .models import SalesInvoice


class SalesInvoiceApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="invoice-admin@example.com",
            password="Strong-test-password-123!",
        )
        cls.customer = Customer.objects.create(
            name="Invoice Customer",
            email="invoice-customer@example.com",
            phone="0500000000",
        )
        cls.service_one = Service.objects.create(
            name="Visa Service",
            service_charge="100.00",
            government_fee="25.00",
        )
        cls.service_two = Service.objects.create(
            name="Typing Service",
            service_charge="50.00",
            government_fee="10.00",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def payload(self):
        today = date.today()
        return {
            "invoice_date": today.isoformat(),
            "customer": self.customer.id,
            "items": [
                {
                    "service": self.service_one.id,
                    "description": "Main application",
                    "sub_fee": "25.00",
                    "service_fee": "100.00",
                    "quantity": 2,
                    "start_date": today.isoformat(),
                    "expiry_date": (today + timedelta(days=30)).isoformat(),
                },
                {
                    "service": self.service_two.id,
                    "description": "Document typing",
                    "sub_fee": "10.00",
                    "service_fee": "50.00",
                    "quantity": 1,
                    "start_date": today.isoformat(),
                    "expiry_date": (today + timedelta(days=10)).isoformat(),
                },
            ],
            "discount_amount": "20.00",
            "received_amount": "100.00",
            "paid_by_staff": False,
            "notes": "Invoice note",
        }

    def test_anonymous_invoice_list_is_rejected(self):
        response = self.client.get("/api/sales-invoices/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_invoice_with_generated_number_and_totals(self):
        self.authenticate()

        response = self.client.post("/api/sales-invoices/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["invoice_number"], "001")
        self.assertEqual(response.data["subtotal"], "310.00")
        self.assertEqual(response.data["total_amount"], "290.00")
        self.assertEqual(response.data["balance_amount"], "190.00")
        self.assertEqual(len(response.data["items"]), 2)
        self.assertEqual(response.data["items"][0]["line_total"], "250.00")

        invoice = SalesInvoice.objects.get()
        self.assertEqual(invoice.invoice_number, "001")

    def test_admin_can_update_invoice_items_and_amounts(self):
        self.authenticate()
        create_response = self.client.post(
            "/api/sales-invoices/", self.payload(), format="json"
        )
        invoice_id = create_response.data["id"]
        today = date.today().isoformat()

        response = self.client.patch(
            f"/api/sales-invoices/{invoice_id}/",
            {
                "items": [
                    {
                        "service": self.service_two.id,
                        "description": "Updated service",
                        "sub_fee": "10.00",
                        "service_fee": "50.00",
                        "quantity": 3,
                        "start_date": today,
                        "expiry_date": today,
                    }
                ],
                "discount_amount": "5.00",
                "received_amount": "20.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["invoice_number"], "001")
        self.assertEqual(response.data["subtotal"], "180.00")
        self.assertEqual(response.data["total_amount"], "175.00")
        self.assertEqual(response.data["balance_amount"], "155.00")
        self.assertEqual(len(response.data["items"]), 1)

    def test_admin_can_soft_delete_invoice_and_list_hides_it(self):
        self.authenticate()
        create_response = self.client.post(
            "/api/sales-invoices/", self.payload(), format="json"
        )
        invoice_id = create_response.data["id"]

        response = self.client.delete(f"/api/sales-invoices/{invoice_id}/")

        self.assertEqual(response.status_code, 204)
        invoice = SalesInvoice.objects.get(pk=invoice_id)
        self.assertTrue(invoice.is_deleted)
        self.assertIsNotNone(invoice.deleted_at)
        self.assertEqual(self.client.get("/api/sales-invoices/").data, [])

    def test_invoice_requires_at_least_one_item(self):
        self.authenticate()
        payload = self.payload()
        payload["items"] = []

        response = self.client.post("/api/sales-invoices/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("items", response.data)

    def test_staff_endpoint_returns_active_admin_users(self):
        self.authenticate()

        response = self.client.get("/api/sales-invoices/staff/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["email"], self.user.email)
        self.assertIn("name", response.data[0])
