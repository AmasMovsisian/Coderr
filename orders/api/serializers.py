from rest_framework import serializers
from orders.models import Order
from offers.models import OfferDetail


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context["request"]
        offer_detail_id = validated_data["offer_detail_id"]

        try:
            offer_detail = OfferDetail.objects.select_related(
                "offer",
                "offer__user"
            ).get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError({
                "offer_detail_id": "OfferDetail not found"
            })

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status="in_progress"
        )

        return order

    def to_representation(self, instance):
        return OrderListSerializer(instance).data


class OrderPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        allowed = ["in_progress", "completed", "cancelled"]

        if value not in allowed:
            raise serializers.ValidationError("Invalid status")

        return value
