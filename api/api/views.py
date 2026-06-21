from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Avg

from reviews.models import Review
from profiles.models import Profile
from offers.models import Offer


class BaseInfoView(APIView):
    """API view that provides aggregated base statistics for the platform."""

    permission_classes = []

    def get(self, request):
        """Return summary metrics including reviews, ratings, profiles, and offers."""

        review_count = Review.objects.count()
        average_rating = (
            Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0
        )
        business_profile_count = Profile.objects.filter(
            user__type="business"
        ).count()
        offer_count = Offer.objects.count()

        return Response({
            "review_count": review_count,
            "average_rating": round(average_rating, 1),
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        })
