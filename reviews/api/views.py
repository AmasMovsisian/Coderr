from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reviews.models import Review
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewPatchSerializer,
)
from .permissions import (
    IsCustomerUser,
    IsReviewOwner
)


class ReviewListCreateView(generics.ListCreateAPIView):
    """API view to list and create reviews."""

    queryset = Review.objects.all()

    def get_serializer_class(self):
        """Return serializer class based on request method."""
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_serializer_context(self):
        """Provide additional context to serializer."""
        return {"request": self.request}

    def get_permissions(self):
        """Assign permissions based on request method."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Return filtered and optionally ordered queryset of reviews."""
        queryset = Review.objects.all()

        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")
        ordering = self.request.query_params.get("ordering")

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        if ordering in ["updated_at", "rating"]:
            queryset = queryset.order_by(ordering)

        return queryset


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, or delete a single review."""

    queryset = Review.objects.all()

    def get_serializer_class(self):
        """Return serializer class based on request method."""
        if self.request.method == "PATCH":
            return ReviewPatchSerializer
        return ReviewSerializer

    def get_permissions(self):
        """Assign permissions based on request method."""
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsReviewOwner()]
        return [IsAuthenticated()]
