from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model.

    Extends Django's default UserAdmin to support custom fields
    like 'type' (customer / business) and improves admin usability
    with filtering, search, and structured field layout.
    """

    list_display = (
        "id",
        "username",
        "email",
        "type",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "type",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "id",
        "username",
        "email",
    )

    ordering = ("id",)

    readonly_fields = (
        "id",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        ("User Identity", {
            "fields": ("id", "username", "password")
        }),
        ("Personal Info", {
            "fields": ("email", "type")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )