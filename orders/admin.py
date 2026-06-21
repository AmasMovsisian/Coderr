from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for order management.
    """

    list_display = (
        "id",
        "title",
        "customer_user",
        "business_user",
        "price",
        "status",
        "offer_type",
        "delivery_time_in_days",
        "created_at",
    )

    list_filter = (
        "status",
        "offer_type",
        "created_at",
    )

    search_fields = (
        "title",
        "customer_user__username",
        "business_user__username",
        "customer_user__email",
        "business_user__email",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "title",
                    "status",
                    "offer_type",
                )
            },
        ),
        (
            "Users",
            {
                "fields": (
                    "customer_user",
                    "business_user",
                )
            },
        ),
        (
            "Pricing & Delivery",
            {
                "fields": (
                    "price",
                    "revisions",
                    "delivery_time_in_days",
                )
            },
        ),
        (
            "Features",
            {
                "fields": ("features",)
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
