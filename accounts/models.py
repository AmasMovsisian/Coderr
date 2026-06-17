from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER_TYPES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    type = models.CharField(
        max_length=20,
        choices=USER_TYPES
    )