from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """Permission allowing access only to authenticated customer users."""

    def has_permission(self, request, view):
        """Check if the user is authenticated and has customer role."""
        return request.user.is_authenticated and request.user.type == "customer"


class IsReviewOwner(BasePermission):
    """Permission allowing access only to the owner of a review."""

    def has_object_permission(self, request, view, obj):
        """Check if the requesting user is the reviewer of the object."""
        return obj.reviewer == request.user
