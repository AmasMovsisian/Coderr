from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from tests.base import BaseAPITestCase


User = get_user_model()


class LoginTests(BaseAPITestCase):
    """Test suite for login endpoint."""

    def setUp(self):
        """Set up test data for login tests."""
        self.url = "/api/login/"
        self.user = User.objects.create_user(
            username="login_test_user",
            email="login_test@test.de",
            password="test123456",
            type="customer"
        )

    def test_login_success(self):
        """Test successful login with correct credentials."""
        payload = {
            "username": "login_test_user",
            "password": "test123456"
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "login_test_user")

    def test_login_wrong_password(self):
        """Test login with incorrect password."""
        payload = {
            "username": "login_test_user",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with non-existent username."""
        payload = {
            "username": "nonexistent_user_12345",
            "password": "test123456"
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        payload = {
            "username": "login_test_user"
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)