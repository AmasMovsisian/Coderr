from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    Store additional profile information for a user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    file = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    tel = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    description = models.TextField(
        blank=True,
        default=""
    )

    working_hours = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """
        Return the username associated with this profile.
        """
        return self.user.username
