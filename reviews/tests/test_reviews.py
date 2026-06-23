from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from reviews.models import Review
from tests.base import BaseAPITestCase


User = get_user_model()


class ReviewTests(BaseAPITestCase):
    """Test suite for review endpoints."""

    def setUp(self):
        """Set up test data for review tests."""
        self.business, self.business_token = self.create_business()
        self.customer, self.customer_token = self.create_customer()
        self.customer2, self.customer2_token = self.create_customer()
        self.reviews_url = "/api/reviews/"
        self.review_payload = {
            "business_user": self.business.id,
            "rating": 5,
            "description": "Excellent service!"
        }

    def test_create_review_success(self):
        """Test successful review creation."""
        self.authenticate(self.customer_token)
        response = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["reviewer"], self.customer.id)
        self.assertEqual(response.data["rating"], 5)

    def test_create_review_duplicate(self):
        """Test duplicate review prevention for same business."""
        self.authenticate(self.customer_token)
        response1 = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_cannot_create_review(self):
        """Test that business users lack permission to create reviews."""
        self.authenticate(self.business_token)
        response = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_create_review(self):
        """Test that unauthenticated users cannot create reviews."""
        self.unauthenticate()
        response = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_invalid_rating(self):
        """Test review creation with rating above maximum."""
        self.authenticate(self.customer_token)
        invalid_payload = {
            "business_user": self.business.id,
            "rating": 6,
            "description": "Invalid rating"
        }
        response = self.client.post(
            self.reviews_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    def test_create_review_rating_too_low(self):
        """Test review creation with rating below minimum."""
        self.authenticate(self.customer_token)
        invalid_payload = {
            "business_user": self.business.id,
            "rating": 0,
            "description": "Invalid rating"
        }
        response = self.client.post(
            self.reviews_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    def test_review_list_all(self):
        """Test listing all reviews."""
        self.authenticate(self.customer_token)
        self.client.post(self.reviews_url, self.review_payload, format="json")
        self.authenticate(self.customer2_token)
        payload2 = {
            "business_user": self.business.id,
            "rating": 4,
            "description": "Good service"
        }
        self.client.post(self.reviews_url, payload2, format="json")
        self.authenticate(self.customer_token)
        response = self.client.get(self.reviews_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_review_list_unauthenticated(self):
        """Test that unauthenticated users cannot list reviews."""
        self.unauthenticate()
        response = self.client.get(self.reviews_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_list_filter_by_business(self):
        """Test filtering reviews by business_user_id."""
        self.authenticate(self.customer_token)
        self.client.post(self.reviews_url, self.review_payload, format="json")
        other_business, other_token = self.create_business()
        self.authenticate(self.customer_token)
        payload = {
            "business_user": other_business.id,
            "rating": 4,
            "description": "Good service"
        }
        self.client.post(self.reviews_url, payload, format="json")
        response = self.client.get(
            f"{self.reviews_url}?business_user_id={self.business.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business.id)

    def test_review_list_filter_by_reviewer(self):
        """Test filtering reviews by reviewer_id."""
        self.authenticate(self.customer_token)
        self.client.post(self.reviews_url, self.review_payload, format="json")
        self.authenticate(self.customer2_token)
        payload2 = {
            "business_user": self.business.id,
            "rating": 4,
            "description": "Good service"
        }
        self.client.post(self.reviews_url, payload2, format="json")
        self.authenticate(self.customer_token)
        response = self.client.get(
        f"{self.reviews_url}?reviewer_id={self.customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reviewer"], self.customer.id)

    def test_review_list_order_by_rating(self):
        """Test ordering reviews by rating."""
        self.authenticate(self.customer_token)
        self.client.post(self.reviews_url, self.review_payload, format="json")
        self.authenticate(self.customer2_token)
        payload2 = {
            "business_user": self.business.id,
            "rating": 3,
            "description": "Okay service"
        }
        self.client.post(self.reviews_url, payload2, format="json")
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.reviews_url}?ordering=rating")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["rating"], 3)
        self.assertEqual(response.data[1]["rating"], 5)

    def test_review_retrieve_success(self):
        """Test retrieving a specific review."""
        self.authenticate(self.customer_token)
        create = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        response = self.client.get(f"{self.reviews_url}{review_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], review_id)
        self.assertEqual(response.data["rating"], 5)

    def test_review_retrieve_unauthenticated(self):
        """Test that unauthenticated users cannot retrieve reviews."""
        self.unauthenticate()
        response = self.client.get(f"{self.reviews_url}1/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_success(self):
        """Test updating a review successfully."""
        self.authenticate(self.customer_token)
        create = self.client.post(
        self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        patch_payload = {
            "rating": 4,
            "description": "Updated review"
        }
        response = self.client.patch(
        f"{self.reviews_url}{review_id}/", patch_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(response.data["description"], "Updated review")

    def test_patch_review_partial(self):
        """Test partial update of a review."""
        self.authenticate(self.customer_token)
        create = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        patch_payload = {"rating": 3}
        response = self.client.patch(
            f"{self.reviews_url}{review_id}/", patch_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 3)
        self.assertEqual(response.data["description"], "Excellent service!")

    def test_patch_review_not_owner(self):
        """Test that only owners can update their reviews."""
        self.authenticate(self.customer_token)
        create = self.client.post(
            self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        self.authenticate(self.customer2_token)
        patch_payload = {"rating": 3}
        response = self.client.patch(
        f"{self.reviews_url}{review_id}/", patch_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_unauthenticated(self):
        """Test that unauthenticated users cannot update reviews."""
        self.authenticate(self.customer_token)
        create = self.client.post(
        self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        self.unauthenticate()
        patch_payload = {"rating": 3}
        response = self.client.patch(
        f"{self.reviews_url}{review_id}/", patch_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_invalid_rating(self):
        """Test updating a review with invalid rating."""
        self.authenticate(self.customer_token)
        create = self.client.post(
        self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        patch_payload = {"rating": 6}
        response = self.client.patch(
        f"{self.reviews_url}{review_id}/", patch_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    def test_delete_review_success(self):
        """Test deleting a review successfully."""
        self.authenticate(self.customer_token)
        create = self.client.post(
        self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        response = self.client.delete(f"{self.reviews_url}{review_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_review_not_owner(self):
        """Test that only owners can delete their reviews."""
        self.authenticate(self.customer_token)
        create = self.client.post(
        self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        self.authenticate(self.customer2_token)
        response = self.client.delete(f"{self.reviews_url}{review_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_unauthenticated(self):
        """Test that unauthenticated users cannot delete reviews."""
        self.authenticate(self.customer_token)
        create = self.client.post(
        self.reviews_url, self.review_payload, format="json")
        review_id = create.data["id"]
        self.unauthenticate()
        response = self.client.delete(f"{self.reviews_url}{review_id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_not_found(self):
        """Test retrieving a non-existent review."""
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.reviews_url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
