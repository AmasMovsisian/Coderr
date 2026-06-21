from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """
    Allow access only to authenticated customer users.
    """

    def has_permission(self, request, view):
        """
        Verify that the user is an authenticated customer.
        """
        return (
            request.user.is_authenticated and
            request.user.type == "customer"
        )


class IsBusinessUser(BasePermission):
    """
    Allow access only to authenticated business users.
    """

    def has_permission(self, request, view):
        """
        Verify that the user is an authenticated business user.
        """
        return (
            request.user.is_authenticated and
            request.user.type == "business"
        )


class IsOrderBusinessOwner(BasePermission):
    """
    Allow access only to the business owner of an order.
    """

    def has_object_permission(self, request, view, obj):
        """
        Verify ownership of the requested order.
        """
        return obj.business_user == request.user


class IsOrderStaff(BasePermission):
    """
    Allow access only to authenticated staff users.
    """

    def has_permission(self, request, view):
        """
        Verify that the user has staff privileges.
        """
        return (
            request.user.is_authenticated and
            request.user.is_staff
        )
