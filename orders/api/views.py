from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q
from django.contrib.auth import get_user_model

from orders.models import Order

from .serializers import (
    OrderListSerializer,
    OrderCreateSerializer,
    OrderPatchSerializer
)

from .permissions import (
    IsCustomerUser,
    IsBusinessUser,
    IsOrderBusinessOwner,
    IsOrderStaff
)

User = get_user_model()


class OrderListCreateView(generics.ListCreateAPIView):

    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        return Order.objects.filter(
            Q(customer_user=user) |
            Q(business_user=user)
        ).order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderListSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]


class OrderPatchView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return OrderPatchSerializer
        return OrderListSerializer

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsBusinessUser(), IsOrderBusinessOwner()]

        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsOrderStaff()]

        return [IsAuthenticated()]


class OrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated, IsOrderStaff]


class OrderCountView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):

        # FIX: check real user (not orders)
        if not User.objects.filter(id=business_user_id).exists():
            return Response(
                {"detail": "Business user not found"},
                status=404
            )

        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="in_progress"
        ).count()

        return Response({"order_count": count})


class CompletedOrderCountView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):

        # FIX: check real user (not orders)
        if not User.objects.filter(id=business_user_id).exists():
            return Response(
                {"detail": "Business user not found"},
                status=404
            )

        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="completed"
        ).count()

        return Response({"completed_order_count": count})
