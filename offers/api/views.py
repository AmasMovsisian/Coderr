from django.db.models import Min

from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

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
    page_size = 6
    page_size_query_param = "page_size"


class OfferListCreateView(generics.ListCreateAPIView):
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
            queryset = queryset.filter(
                details__delivery_time_in_days__lte=max_delivery_time
            )
        if ordering == "min_price":
            queryset = queryset.order_by("min_price")
        return queryset.distinct()

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                IsBusinessUser(),
            ]
        return []

    def get_serializer_class(self):

        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [
            IsAuthenticated(),
            IsOfferOwner(),
        ]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return OfferPatchSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
