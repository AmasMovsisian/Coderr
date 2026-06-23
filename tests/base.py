from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from profiles.models import Profile


User = get_user_model()


class BaseAPITestCase(APITestCase):
    """Base test case with helper methods for user creation and authentication."""

    def create_customer(self):
        """Create and return a customer user with unique credentials."""
        import time
        import random
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        user = User.objects.create_user(
            username=f"customer_{unique_id}",
            email=f"customer_{unique_id}@test.de",
            password="test123456",
            type="customer"
        )
        Profile.objects.create(user=user)
        token = Token.objects.create(user=user)
        return user, token

    def create_business(self):
        """Create and return a business user with unique credentials."""
        import time
        import random
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        user = User.objects.create_user(
            username=f"business_{unique_id}",
            email=f"business_{unique_id}@test.de",
            password="test123456",
            type="business"
        )
        Profile.objects.create(user=user)
        token = Token.objects.create(user=user)
        return user, token

    def authenticate(self, token):
        """Set the authentication token for the test client."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def unauthenticate(self):
        """Remove authentication credentials from the test client."""
        self.client.credentials()
