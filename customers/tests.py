from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Customer


class CustomerApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="staff@example.com",
            password="Strong-test-password-123!",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_anonymous_customer_list_is_rejected(self):
        response = self.client.get("/api/customers/")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_non_staff_customer_list_is_rejected(self):
        non_staff_user = get_user_model().objects.create_user(
            email="user@example.com",
            password="Strong-test-password-123!",
        )
        self.client.force_authenticate(user=non_staff_user)

        response = self.client.get("/api/customers/")

        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_create_customer_with_requested_fields(self):
        self.authenticate()
        payload = {
            "name": "Amina Rahman",
            "email": "amina@example.com",
            "phone": "+971501234567",
            "address_line_1": "Office 12",
            "address_line_2": "Al Nahda",
            "address_line_3": "Dubai",
            "bank_name": "Example Bank",
            "account_holder_name": "Amina Rahman",
            "account_number": "1234567890",
            "swift_address": "SWIFT-ADDRESS-1",
            "iban": "AE070331234567890123456",
            "trn": "TRN-123456789",
            "notes": "Preferred contact by email.",
        }

        response = self.client.post("/api/customers/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.get()
        self.assertEqual(customer.name, payload["name"])
        self.assertEqual(customer.account_number, payload["account_number"])
        self.assertEqual(customer.swift_address, payload["swift_address"])
        self.assertEqual(customer.iban, payload["iban"])
        self.assertEqual(customer.trn, payload["trn"])
        self.assertEqual(response.data["email"], payload["email"])

    def test_customer_create_requires_name_email_and_phone(self):
        self.authenticate()

        response = self.client.post("/api/customers/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertCountEqual(response.data.keys(), ["name", "email", "phone"])

    def test_authenticated_customer_list_is_newest_first_and_minimal(self):
        self.authenticate()
        Customer.objects.create(
            name="Older Customer",
            email="older@example.com",
            phone="1111111111",
            account_number="do-not-list-this",
        )
        Customer.objects.create(
            name="Newer Customer",
            email="newer@example.com",
            phone="2222222222",
            account_number="do-not-list-this-either",
        )

        response = self.client.get("/api/customers/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["name"], "Newer Customer")
        self.assertEqual(
            set(response.data[0]),
            {"id", "name", "email", "phone", "created_at", "updated_at"},
        )

    def test_authenticated_admin_can_view_customer_details(self):
        self.authenticate()
        customer = Customer.objects.create(
            name="Detailed Customer",
            email="detail@example.com",
            phone="4444444444",
            address_line_1="Office 1",
            bank_name="Example Bank",
            account_number="1234567890",
            swift_address="SWIFT-ADDRESS-2",
            iban="AE070331234567890123456",
            trn="TRN-987654321",
            notes="Detail note",
        )

        response = self.client.get(f"/api/customers/{customer.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], customer.name)
        self.assertEqual(response.data["iban"], customer.iban)
        self.assertEqual(response.data["notes"], customer.notes)

    def test_authenticated_admin_can_soft_delete_customer(self):
        self.authenticate()
        customer = Customer.objects.create(
            name="Delete Customer",
            email="delete@example.com",
            phone="5555555555",
        )

        response = self.client.delete(f"/api/customers/{customer.id}/")

        self.assertEqual(response.status_code, 204)
        customer.refresh_from_db()
        self.assertTrue(customer.is_deleted)
        self.assertIsNotNone(customer.deleted_at)

        list_response = self.client.get("/api/customers/")

        self.assertEqual(list_response.status_code, 200)
        self.assertNotIn(customer.id, [item["id"] for item in list_response.data])

    def test_authenticated_admin_can_edit_customer(self):
        self.authenticate()
        customer = Customer.objects.create(
            name="Before Edit",
            email="edit@example.com",
            phone="6666666666",
        )

        response = self.client.patch(
            f"/api/customers/{customer.id}/",
            {"name": "After Edit", "iban": "AE070331234567890123456"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        customer.refresh_from_db()
        self.assertEqual(customer.name, "After Edit")
        self.assertEqual(customer.iban, "AE070331234567890123456")

    def test_admin_can_open_customer_list(self):
        Customer.objects.create(
            name="Admin Visible Customer",
            email="visible@example.com",
            phone="3333333333",
        )
        self.client.force_login(self.user)

        response = self.client.get("/ajfan-documents/customers/customer/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Visible Customer")

        add_response = self.client.get("/ajfan-documents/customers/customer/add/")

        self.assertEqual(add_response.status_code, 200)
