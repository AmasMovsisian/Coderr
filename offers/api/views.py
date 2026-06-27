from django.db.models import Min

from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from offers.models import Offer
from offers.models import OfferDetail

from .permissions import IsBusinessUser
from .permissions import IsOfferOwner

from .serializers import OfferListSerializer
from .serializers import OfferRetrieveSerializer
from .serializers import OfferCreateSerializer
from .serializers import OfferPatchSerializer
from .serializers import OfferDetailSerializer


class OfferPagination(PageNumberPagination):
    """Custom pagination class for offers list endpoint."""
    page_size = 6
    page_size_query_param = "page_size"


class OfferListCreateView(generics.ListCreateAPIView):
    """Handles listing all offers and creating new offers with filtering, searching and ordering support."""

    pagination_class = OfferPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "title",
        "description",
    ]
    ordering_fields = [
        "updated_at",
        "min_price",
    ]

    def get_queryset(self):
        """
        Return filtered and annotated queryset of offers.

        Supports filtering by creator, minimum price, and maximum delivery time.
        Also supports ordering by annotated minimum price.
        """
        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days")
        )
        creator_id = self.request.query_params.get("creator_id")
        min_price = self.request.query_params.get("min_price")
        max_delivery_time = self.request.query_params.get("max_delivery_time")
        ordering = self.request.query_params.get("ordering")

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)
        if max_delivery_time:
            try:
                max_delivery_time_int = int(max_delivery_time)
            except ValueError:
                raise ValidationError({"max_delivery_time": "Must be an integer."})
            queryset = queryset.filter(
                details__delivery_time_in_days__lte=max_delivery_time_int
            )
        if ordering == "min_price":
            queryset = queryset.order_by("min_price")

        return queryset.distinct().order_by("-created_at")

    def get_permissions(self):
        """
        Return permissions based on request method.

        GET requests are public.
        POST requests require authentication and business user role.
        """
        if self.request.method == "GET":
            return [AllowAny()]
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                IsBusinessUser(),
            ]
        return []

    def get_serializer_class(self):
        """
        Return serializer class depending on request method.

        POST uses creation serializer, otherwise list serializer.
        """
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def get_serializer_context(self):
        """
        Ensure request context is passed to serializer.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """
        Create Offer and return full create representation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        return Response(
            OfferCreateSerializer(
                offer,
                context=self.get_serializer_context()
            ).data,
            status=201
        )


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific offer instance."""

    def get_queryset(self):
        """
        Return queryset with annotated min_price and min_delivery_time.
        """
        return Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days")
        )

    def get_permissions(self):
        """
        Return permissions depending on request method.

        GET requires authentication only.
        Modifying requests require ownership permission.
        """
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [
            IsAuthenticated(),
            IsOfferOwner(),
        ]

    def get_serializer_class(self):
        """
        Return serializer class depending on request method.

        PATCH uses partial update serializer, otherwise retrieve serializer.
        """
        if self.request.method == "PATCH":
            return OfferPatchSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Retrieve a single offer detail instance."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]