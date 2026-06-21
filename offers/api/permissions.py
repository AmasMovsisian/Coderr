from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """Permission that allows access only to authenticated business users."""

    def has_permission(self, request, view):
        """
        Check if the requesting user is authenticated and has business role.
        """
        return (
            request.user.is_authenticated
            and request.user.type == "business"
        )


class IsOfferOwner(BasePermission):
    """Permission that allows access only to the owner of an Offer object."""

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user is the owner of the object.
        """
        return obj.user == request.user
