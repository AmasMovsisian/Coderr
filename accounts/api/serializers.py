from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration.

    Validates password confirmation and creates a new user instance
    using the custom user model manager.
    """
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        )
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate(self, attrs):
        """
        Validates that the provided password and repeated password match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"error": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        """
        Creates and returns a new user instance after removing
        the repeated password field.
        """
        validated_data.pop("repeated_password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            type=validated_data["type"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user with username and password.

    Validates credentials using Django's authentication system and
    attaches the authenticated user to validated data.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validates user credentials and returns authenticated user
        if credentials are correct.
        """
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"]
        )
        if not user:
            raise serializers.ValidationError(
                {"error": "Invalid credentials"}
            )
        attrs["user"] = user
        return attrs
