from rest_framework import serializers
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for representing Review instances."""

    class Meta:
        """Meta options for ReviewSerializer."""
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at"
        ]


class ReviewRatingValidationMixin:
    """Mixin providing validation logic for review rating fields."""

    def validate_rating(self, value):
        """Validate that rating is within the allowed range (1–5)."""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value


class ReviewCreateSerializer(
    ReviewRatingValidationMixin,
    serializers.ModelSerializer
):
    """Serializer for creating Review instances."""

    class Meta:
        """Meta options for ReviewCreateSerializer."""
        model = Review
        fields = [
            "business_user",
            "rating",
            "description"
        ]

    def validate(self, data):
        """Check that user hasn't already reviewed this business."""
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            business_user = data.get("business_user")

            if Review.objects.filter(
                business_user=business_user,
                reviewer=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this business."
                )

        return data

    def create(self, validated_data):
        """Create a new Review instance using the authenticated user as reviewer."""
        request = self.context["request"]

        return Review.objects.create(
            reviewer=request.user,
            **validated_data
        )

    def to_representation(self, instance):
        """Return serialized representation using the default ReviewSerializer."""
        return ReviewSerializer(instance).data


class ReviewPatchSerializer(
    ReviewRatingValidationMixin,
    serializers.ModelSerializer
):
    """Serializer for partially updating Review instances."""

    class Meta:
        """Meta options for ReviewPatchSerializer."""
        model = Review
        fields = [
            "rating",
            "description"
        ]
