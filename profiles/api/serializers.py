from rest_framework import serializers
from ..models import Profile


class ProfileDetailSerializer(serializers.ModelSerializer):
    """
    Full profile representation with editable user fields.
    """

    user = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    type = serializers.CharField(source="user.type", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True)
    email = serializers.EmailField(source="user.email", required=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]

    def update(self, instance, validated_data):
        """
        Update profile and related user fields.
        """
        user_data = validated_data.pop("user", {})
        user = instance.user

        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.email = validated_data.get("email", user.email)
        user.save()

        instance.location = validated_data.get("location", instance.location)
        instance.tel = validated_data.get("tel", instance.tel)
        instance.description = validated_data.get(
            "description", instance.description)
        instance.working_hours = validated_data.get(
            "working_hours", instance.working_hours)

        if "file" in validated_data:
            instance.file = validated_data["file"]

        instance.save()
        return instance


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Lightweight profile representation for business users.
    """

    user = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    type = serializers.CharField(source="user.type", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True, default="")
    last_name = serializers.CharField(
        source="user.last_name", read_only=True, default="")

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Minimal profile representation for customer-facing views.
    """

    user = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    type = serializers.CharField(source="user.type", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True, default="")
    last_name = serializers.CharField(
        source="user.last_name", read_only=True, default="")
    uploaded_at = serializers.DateTimeField(
        source="created_at", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
