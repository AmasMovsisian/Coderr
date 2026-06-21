from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from .serializers import (
    ProfileDetailSerializer,
    BusinessProfileSerializer,
    CustomerProfileSerializer
)
from .permissions import IsProfileOwner


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update a single user profile.
    """

    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileDetailSerializer

    def get_serializer_class(self):
        return ProfileDetailSerializer

    def get_object(self):
        """
        Return profile by user id from URL parameter.
        """
        return get_object_or_404(Profile, user_id=self.kwargs["pk"])

    def perform_update(self, serializer):
        """
        Ensure only the profile owner can update the profile.
        """
        profile = self.get_object()

        if self.request.user != profile.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()

        serializer.save()


class BusinessProfileListView(generics.ListAPIView):
    """
    List all business profiles.
    """

    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return profiles filtered by business user type.
        """
        return Profile.objects.filter(user__type="business")


class CustomerProfileListView(generics.ListAPIView):
    """
    List all customer profiles.
    """

    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return profiles filtered by customer user type.
        """
        return Profile.objects.filter(user__type="customer")
