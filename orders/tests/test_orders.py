from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse
from orders.models import Order
from offers.models import Offer, OfferDetail
from tests.base import BaseAPITestCase


User = get_user_model()


class OrderTests(BaseAPITestCase):
    """Test suite for order endpoints."""

    def setUp(self):
        """Set up test data for order tests."""
        self.business, self.business_token = self.create_business()
        self.customer, self.customer_token = self.create_customer()
        self.orders_url = "/api/orders/"
        self.order_count_url = "/api/order-count/"
        self.completed_order_count_url = "/api/completed-order-count/"
        self.offer_payload = {
            "title": "Logo Design Service",
            "description": "Professional logo design service",
            "details": [
                {
                    "title": "Basic Logo",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": 50.00,
                    "features": ["Logo Design"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Logo",
                    "revisions": 3,
                    "delivery_time_in_days": 5,
                    "price": 100.00,
                    "features": ["Logo Design", "Business Card"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Logo",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200.00,
                    "features": ["Logo Design", "Business Card", "Letterhead"],
                    "offer_type": "premium"
                }
            ]
        }
        self.authenticate(self.business_token)
        response = self.client.post("/api/offers/", self.offer_payload, format="json")
        self.offer_id = response.data["id"]
        self.offer = Offer.objects.get(id=self.offer_id)
        self.offer_detail = self.offer.details.first()
        self.authenticate(self.customer_token)
        self.order_payload = {
            "offer_detail_id": self.offer_detail.id
        }
        response = self.client.post(self.orders_url, self.order_payload, format="json")
        self.order_id = response.data["id"]

    def test_create_order_success(self):
        """Test successful order creation."""
        self.authenticate(self.customer_token)
        self.authenticate(self.business_token)
        response = self.client.post("/api/offers/", self.offer_payload, format="json")
        offer_id = response.data["id"]
        offer = Offer.objects.get(id=offer_id)
        offer_detail = offer.details.first()
        self.authenticate(self.customer_token)
        payload = {"offer_detail_id": offer_detail.id}
        response = self.client.post(self.orders_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_business_cannot_create_order(self):
        """Test that business users cannot create orders."""
        self.authenticate(self.business_token)
        payload = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(self.orders_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_create_order(self):
        """Test that unauthenticated users cannot create orders."""
        self.unauthenticate()
        payload = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(self.orders_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_invalid_offer_detail(self):
        """Test order creation with invalid offer_detail_id."""
        self.authenticate(self.customer_token)
        payload = {"offer_detail_id": 99999}
        response = self.client.post(self.orders_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("offer_detail_id", response.data)

    def test_order_list_customer(self):
        """Test listing orders as a customer."""
        self.authenticate(self.customer_token)
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["customer_user"], self.customer.id)

    def test_order_list_business(self):
        """Test listing orders as a business user."""
        self.authenticate(self.business_token)
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business.id)

    def test_order_list_unauthenticated(self):
        """Test that unauthenticated users cannot list orders."""
        self.unauthenticate()
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_status_success(self):
        """Test successful order status update."""
        self.authenticate(self.business_token)
        payload = {"status": "completed"}
        response = self.client.patch(f"{self.orders_url}{self.order_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_patch_order_status_invalid(self):
        """Test order status update with invalid status."""
        self.authenticate(self.business_token)
        payload = {"status": "invalid_status"}
        response = self.client.patch(f"{self.orders_url}{self.order_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_not_owner(self):
        """Test that businesses cannot update orders from other businesses."""
        other_business, other_token = self.create_business()
        self.authenticate(other_token)
        payload = {"status": "completed"}
        response = self.client.patch(f"{self.orders_url}{self.order_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_customer_cannot_update(self):
        """Test that customers cannot update order status."""
        self.authenticate(self.customer_token)
        payload = {"status": "completed"}
        response = self.client.patch(f"{self.orders_url}{self.order_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_as_staff(self):
        """Test order deletion by staff user."""
        staff_user = User.objects.create_user(
            username="staff",
            email="staff@test.de",
            password="test123456",
            type="business",
            is_staff=True
        )
        staff_token = Token.objects.create(user=staff_user)
        self.authenticate(staff_token)
        response = self.client.delete(f"{self.orders_url}{self.order_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_order_as_non_staff(self):
        """Test that non-staff users cannot delete orders."""
        self.authenticate(self.business_token)
        response = self.client.delete(f"{self.orders_url}{self.order_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_not_found(self):
        """Test retrieving a non-existent order."""
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.orders_url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_success(self):
        """Test getting order count for a business user."""
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.order_count_url}{self.business.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 1)

    def test_order_count_business_not_found(self):
        """Test order count with non-existent business user."""
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.order_count_url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_unauthenticated(self):
        """Test order count without authentication."""
        self.unauthenticate()
        response = self.client.get(f"{self.order_count_url}{self.business.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_order_count_success(self):
        """Test getting completed order count for a business user."""
        self.authenticate(self.business_token)
        payload = {"status": "completed"}
        self.client.patch(f"{self.orders_url}{self.order_id}/", payload, format="json")
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.completed_order_count_url}{self.business.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 1)

    def test_completed_order_count_business_not_found(self):
        """Test completed order count with non-existent business user."""
        self.authenticate(self.customer_token)
        response = self.client.get(f"{self.completed_order_count_url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)