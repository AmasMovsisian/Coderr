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
    """
    List user-related orders and create new customer orders.
    """

    pagination_class = None

    def get_queryset(self):
        """
        Return all orders associated with the authenticated user.
        """
        user = self.request.user

        return Order.objects.filter(
            Q(customer_user=user) |
            Q(business_user=user)
        ).order_by("-created_at")

    def get_serializer_class(self):
        """
        Select the appropriate serializer based on the request method.
        """
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderListSerializer

    def get_serializer_context(self):
        """
        Provide request context to the serializer.
        """
        return {"request": self.request}

    def get_permissions(self):
        """
        Apply method-specific permission rules.
        """
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]


class OrderPatchView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an individual order.
    """

    queryset = Order.objects.all()

    def get_serializer_class(self):
        """
        Select the appropriate serializer for the current action.
        """
        if self.request.method == "PATCH":
            return OrderPatchSerializer
        return OrderListSerializer

    def get_permissions(self):
        """
        Apply action-specific permission checks.
        """
        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsBusinessUser(), IsOrderBusinessOwner()]

        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsOrderStaff()]

        return [IsAuthenticated()]


class OrderDeleteView(generics.DestroyAPIView):
    """
    Delete an order with staff-level authorization.
    """

    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated, IsOrderStaff]


class OrderCountView(generics.GenericAPIView):
    """
    Return the number of active orders for a business user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Retrieve the count of in-progress orders.
        """

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
    """
    Return the number of completed orders for a business user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Retrieve the count of completed orders.
        """

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
