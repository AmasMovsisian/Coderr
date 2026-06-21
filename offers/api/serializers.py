from rest_framework import serializers

from offers.models import Offer
from offers.models import OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferDetailUrlSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url",
        ]

    def get_url(self, obj):
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                f"/api/offerdetails/{obj.id}/"
            )

        return f"/api/offerdetails/{obj.id}/"


class OfferListSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(
        source="user.id",
        read_only=True
    )

    details = serializers.SerializerMethodField()

    min_price = serializers.ReadOnlyField()

    min_delivery_time = serializers.ReadOnlyField()

    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_details(self, obj):
        return OfferDetailUrlSerializer(
            obj.details.all(),
            many=True,
            context=self.context
        ).data

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }


class OfferRetrieveSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(
        source="user.id",
        read_only=True
    )

    details = serializers.SerializerMethodField()

    min_price = serializers.ReadOnlyField()

    min_delivery_time = serializers.ReadOnlyField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_details(self, obj):
        return OfferDetailUrlSerializer(
            obj.details.all(),
            many=True,
            context=self.context
        ).data


class OfferCreateSerializer(serializers.ModelSerializer):

    details = OfferDetailSerializer(
        many=True
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]

    def validate_details(self, value):

        if len(value) != 3:
            raise serializers.ValidationError(
                "Exactly 3 details required."
            )

        types = {item["offer_type"] for item in value}

        if types != {"basic", "standard", "premium"}:
            raise serializers.ValidationError(
                "Offer must contain basic, standard and premium."
            )

        return value

    def create(self, validated_data):

        details_data = validated_data.pop("details")

        offer = Offer.objects.create(
            user=self.context["request"].user,
            **validated_data
        )

        for detail in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail
            )

        return offer

    def to_representation(self, instance):

        return {
            "id": instance.id,
            "title": instance.title,
            "image": instance.image.url if instance.image else None,
            "description": instance.description,
            "details": OfferDetailSerializer(
                instance.details.all(),
                many=True
            ).data,
        }


class OfferPatchSerializer(serializers.ModelSerializer):

    details = serializers.ListField(
        required=False
    )

    class Meta:
        model = Offer
        fields = [
            "title",
            "image",
            "description",
            "details",
        ]

    def update(self, instance, validated_data):

        details = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if details:

            for detail_data in details:

                offer_type = detail_data.get("offer_type")

                if not offer_type:
                    continue

                detail = instance.details.filter(
                    offer_type=offer_type
                ).first()

                if not detail:
                    continue

                for key, value in detail_data.items():
                    setattr(detail, key, value)

                detail.save()

        return instance

    def to_representation(self, instance):

        return {
            "id": instance.id,
            "title": instance.title,
            "image": instance.image.url if instance.image else None,
            "description": instance.description,
            "details": OfferDetailSerializer(
                instance.details.all(),
                many=True
            ).data,
        }
