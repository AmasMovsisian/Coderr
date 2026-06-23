from rest_framework import status
from tests.base import BaseAPITestCase


class BaseInfoTests(BaseAPITestCase):
    """Test suite for base-info endpoint."""

    def test_base_info_success(self):
        """Test retrieving base platform information."""
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("review_count", response.data)
        self.assertIn("average_rating", response.data)
        self.assertIn("business_profile_count", response.data)
        self.assertIn("offer_count", response.data)

    def test_base_info_data_types(self):
        """Test base info response contains correct data types."""
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["review_count"], int)
        self.assertIsInstance(response.data["average_rating"], (int, float))
        self.assertIsInstance(response.data["business_profile_count"], int)
        self.assertIsInstance(response.data["offer_count"], int)

    def test_base_info_no_auth_required(self):
        """Test base info is accessible without authentication."""
        self.unauthenticate()
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)