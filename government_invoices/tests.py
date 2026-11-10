from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import Customer
from reminders.models import Reminder
from services.models import Service

from .models import GovernmentInvoice


class GovernmentInvoiceApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="government-invoice-admin@example.com",
            password="Strong-test-password-123!",
        )
        cls.customer = Customer.objects.create(
            name="Government Customer",
            email="government-customer@example.com",
            phone="0500000001",
        )
        cls.service_one = Service.objects.create(
            name="Government Service",
            service_charge="100.00",
            government_fee="25.00",
        )
        cls.service_two = Service.objects.create(
            name="Government Typing",
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
                    "description": "Government application",
                    "government_fee": "25.00",
                    "service_fee": "100.00",
                    "quantity": 2,
                    "start_date": today.isoformat(),
                    "end_date": (today + timedelta(days=30)).isoformat(),
                },
                {
                    "service": self.service_two.id,
                    "description": "Government typing",
                    "government_fee": "10.00",
                    "service_fee": "50.00",
                    "quantity": 1,
                    "start_date": today.isoformat(),
                    "end_date": (today + timedelta(days=10)).isoformat(),
                },
            ],
            "discount_amount": "20.00",
            "received_amount": "100.00",
            "payment_mode": "bank",
            "paid_by_staff": False,
            "notes": "Government invoice note",
        }

    def test_anonymous_government_invoice_list_is_rejected(self):
        response = self.client.get("/api/government-invoices/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_invoice_without_vat_and_calculate_totals(self):
        self.authenticate()

        response = self.client.post("/api/government-invoices/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["invoice_number"], "001")
        self.assertEqual(response.data["subtotal"], "310.00")
        self.assertEqual(response.data["total_amount"], "290.00")
        self.assertEqual(response.data["balance_amount"], "190.00")
        self.assertEqual(response.data["payment_mode"], "bank")
        self.assertEqual(response.data["items"][0]["line_total"], "250.00")
        self.assertNotIn("vat", response.data)

    def test_invoice_item_end_dates_create_automatic_reminders(self):
        self.authenticate()

        response = self.client.post("/api/government-invoices/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        reminders = Reminder.objects.filter(customer=self.customer, is_deleted=False)
        self.assertEqual(reminders.count(), 2)
        self.assertEqual(
            {reminder.reminder_title for reminder in reminders},
            {"Govt. invoice 001: Government Service expiry", "Govt. invoice 001: Government Typing expiry"},
        )

    def test_admin_can_create_sequential_zero_padded_numbers(self):
        self.authenticate()

        first_response = self.client.post(
            "/api/government-invoices/", self.payload(), format="json"
        )
        second_response = self.client.post(
            "/api/government-invoices/", self.payload(), format="json"
        )

        self.assertEqual(first_response.data["invoice_number"], "001")
        self.assertEqual(second_response.data["invoice_number"], "002")

    def test_admin_can_edit_dates_and_lines(self):
        self.authenticate()
        create_response = self.client.post(
            "/api/government-invoices/", self.payload(), format="json"
        )
        invoice_id = create_response.data["id"]
        today = date.today().isoformat()

        response = self.client.patch(
            f"/api/government-invoices/{invoice_id}/",
            {
                "items": [
                    {
                        "service": self.service_two.id,
                        "description": "Updated government line",
                        "government_fee": "10.00",
                        "service_fee": "50.00",
                        "quantity": 3,
                        "start_date": today,
                        "end_date": today,
                    }
                ],
                "discount_amount": "5.00",
                "received_amount": "20.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["subtotal"], "180.00")
        self.assertEqual(response.data["total_amount"], "175.00")
        self.assertEqual(response.data["balance_amount"], "155.00")
        self.assertEqual(response.data["items"][0]["end_date"], today)

    def test_admin_can_soft_delete_government_invoice(self):
        self.authenticate()
        create_response = self.client.post(
            "/api/government-invoices/", self.payload(), format="json"
        )
        invoice_id = create_response.data["id"]

        response = self.client.delete(f"/api/government-invoices/{invoice_id}/")

        self.assertEqual(response.status_code, 204)
        invoice = GovernmentInvoice.objects.get(pk=invoice_id)
        self.assertTrue(invoice.is_deleted)
        self.assertEqual(self.client.get("/api/government-invoices/").data, [])

    def test_government_invoice_requires_at_least_one_line(self):
        self.authenticate()
        payload = self.payload()
        payload["items"] = []

        response = self.client.post("/api/government-invoices/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("items", response.data)
