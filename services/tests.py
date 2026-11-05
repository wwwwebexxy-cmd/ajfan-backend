import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from PIL import Image

from .models import Service


TEST_MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="ajfan-service-tests-"))


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ServiceApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="service-admin@example.com",
            password="Strong-test-password-123!",
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def image_upload(self):
        image = Image.new("RGB", (1, 1), "#09977f")
        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")
        return SimpleUploadedFile("service.png", image_buffer.getvalue(), content_type="image/png")

    def test_authenticated_admin_can_create_service_with_image(self):
        self.authenticate()
        image_buffer = self.image_upload()

        response = self.client.post(
            "/api/services/",
            {
                "name": "Visa Assistance",
                "image": image_buffer,
                "service_charge": "150.00",
                "includes_government_fee": "true",
                "government_fee": "20.00",
                "description": "Application support service.",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        service = Service.objects.get()
        self.assertEqual(service.name, "Visa Assistance")
        self.assertTrue(service.image.name.startswith("services/"))
        self.assertTrue(service.includes_government_fee)

    def test_authenticated_admin_can_edit_service(self):
        self.authenticate()
        service = Service.objects.create(
            name="Old Service",
            service_charge="100.00",
            government_fee="10.00",
        )

        response = self.client.patch(
            f"/api/services/{service.id}/",
            {"name": "Updated Service", "service_charge": "125.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        service.refresh_from_db()
        self.assertEqual(service.name, "Updated Service")
        self.assertEqual(str(service.service_charge), "125.00")

    def test_authenticated_admin_can_soft_delete_service_and_list_hides_it(self):
        self.authenticate()
        service = Service.objects.create(
            name="Delete Service",
            service_charge="80.00",
            government_fee="0.00",
        )

        response = self.client.delete(f"/api/services/{service.id}/")

        self.assertEqual(response.status_code, 204)
        service.refresh_from_db()
        self.assertTrue(service.is_deleted)
        self.assertIsNotNone(service.deleted_at)
        self.assertEqual(self.client.get("/api/services/").data, [])

    def test_anonymous_service_list_is_rejected(self):
        response = self.client.get("/api/services/")

        self.assertEqual(response.status_code, 401)
