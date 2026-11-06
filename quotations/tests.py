from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import Customer
from services.models import Service

from .models import Quotation


class QuotationApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="quotation-admin@example.com",
            password="Strong-test-password-123!",
        )
        cls.customer = Customer.objects.create(
            name="Quotation Customer",
            email="quotation-customer@example.com",
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
            "quotation_date": today.isoformat(),
            "customer": self.customer.id,
            "items": [
                {
                    "service": self.service_one.id,
                    "description": "Main application",
                    "government_fee": "25.00",
                    "service_fee": "100.00",
                    "quantity": 2,
                    "start_date": today.isoformat(),
                    "end_date": (today + timedelta(days=30)).isoformat(),
                },
                {
                    "service": self.service_two.id,
                    "description": "Document typing",
                    "government_fee": "10.00",
                    "service_fee": "50.00",
                    "quantity": 1,
                    "start_date": today.isoformat(),
                    "end_date": (today + timedelta(days=10)).isoformat(),
                },
            ],
            "discount_amount": "20.00",
            "notes": "Quotation note",
        }

    def test_anonymous_quotation_list_is_rejected(self):
        response = self.client.get("/api/quotations/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_quotation_without_vat_and_with_dates(self):
        self.authenticate()

        response = self.client.post("/api/quotations/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["quotation_number"], "001")
        self.assertEqual(response.data["subtotal"], "310.00")
        self.assertEqual(response.data["total_amount"], "290.00")
        self.assertEqual(response.data["items"][0]["line_total"], "250.00")
        self.assertEqual(response.data["items"][0]["start_date"], date.today().isoformat())
        self.assertNotIn("vat", {key.lower() for key in response.data})

    def test_quotation_numbers_are_sequential(self):
        self.authenticate()

        first = self.client.post("/api/quotations/", self.payload(), format="json")
        second = self.client.post("/api/quotations/", self.payload(), format="json")

        self.assertEqual(first.data["quotation_number"], "001")
        self.assertEqual(second.data["quotation_number"], "002")

    def test_admin_can_update_quotation_items_and_discount(self):
        self.authenticate()
        create_response = self.client.post("/api/quotations/", self.payload(), format="json")
        quotation_id = create_response.data["id"]
        today = date.today().isoformat()

        response = self.client.patch(
            f"/api/quotations/{quotation_id}/",
            {
                "items": [
                    {
                        "service": self.service_two.id,
                        "description": "Updated service",
                        "government_fee": "10.00",
                        "service_fee": "50.00",
                        "quantity": 3,
                        "start_date": today,
                        "end_date": today,
                    }
                ],
                "discount_amount": "5.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["quotation_number"], "001")
        self.assertEqual(response.data["subtotal"], "180.00")
        self.assertEqual(response.data["total_amount"], "175.00")
        self.assertEqual(len(response.data["items"]), 1)

    def test_admin_can_soft_delete_quotation_and_list_hides_it(self):
        self.authenticate()
        create_response = self.client.post("/api/quotations/", self.payload(), format="json")
        quotation_id = create_response.data["id"]

        response = self.client.delete(f"/api/quotations/{quotation_id}/")

        self.assertEqual(response.status_code, 204)
        quotation = Quotation.objects.get(pk=quotation_id)
        self.assertTrue(quotation.is_deleted)
        self.assertEqual(self.client.get("/api/quotations/").data, [])

    def test_quotation_requires_at_least_one_item(self):
        self.authenticate()
        payload = self.payload()
        payload["items"] = []

        response = self.client.post("/api/quotations/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("items", response.data)
