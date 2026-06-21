from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """
    Shows OfferDetails inside Offer admin page.
    """
    model = OfferDetail
    extra = 0
    readonly_fields = ("id",)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "title",
        "get_min_price",
        "get_min_delivery_time",
        "updated_at",
        "created_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
        "user",
    )

    search_fields = (
        "id",
        "title",
        "description",
        "user__username",
    )

    ordering = ("-updated_at",)

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "get_min_price",
        "get_min_delivery_time",
    )

    fieldsets = (
        ("Offer Info", {
            "fields": (
                "id",
                "user",
                "title",
                "description",
            )
        }),
        ("Meta Info", {
            "fields": (
                "created_at",
                "updated_at",
                "get_min_price",
                "get_min_delivery_time",
            )
        }),
    )

    inlines = [OfferDetailInline]

    def get_min_price(self, obj):
        detail = obj.details.order_by("price").first()
        return detail.price if detail else 0
    get_min_price.short_description = "Min Price"

    def get_min_delivery_time(self, obj):
        detail = obj.details.order_by("delivery_time_in_days").first()
        return detail.delivery_time_in_days if detail else 0
    get_min_delivery_time.short_description = "Min Delivery Time"


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "offer",
        "title",
        "offer_type",
        "price",
        "delivery_time_in_days",
        "revisions",
    )

    list_filter = (
        "offer_type",
        "price",
        "delivery_time_in_days",
    )

    search_fields = (
        "title",
        "offer__title",
        "offer__user__username",
    )

    ordering = ("offer", "offer_type")
