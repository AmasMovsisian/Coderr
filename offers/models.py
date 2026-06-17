from django.db import models
from django.conf import settings

# Create your models here.


class Offer(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="offers/",
        blank=True,
        null=True
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


class OfferDetail(models.Model):

    offer = models.ForeignKey(
        Offer,
        related_name="details",
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    revisions = models.IntegerField()

    delivery_time_in_days = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    features = models.JSONField()

    offer_type = models.CharField(
        max_length=20
    )
