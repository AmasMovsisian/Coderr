from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """
    Allow access only to the owner of a profile object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check whether the requesting user owns the object.
        """
        return obj.user == request.user