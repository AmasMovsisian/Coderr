from django.db import models
from django.conf import settings


class Review(models.Model):
    """Model representing a review left by a user for a business user."""

    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written"
    )

    rating = models.PositiveSmallIntegerField()
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Review model."""
        unique_together = ["business_user", "reviewer"]

    def __str__(self):
        """Return a string representation of the review."""
        return f"{self.rating} by {self.reviewer}"
