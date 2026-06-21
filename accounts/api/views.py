from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .serializers import RegistrationSerializer, LoginSerializer
from profiles.models import Profile


class RegistrationView(APIView):
    """
    Handle user registration and token creation.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user account and return an authentication token.
        """
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Profile.objects.create(user=user)
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    Authenticate users and provide access tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate credentials and return an authentication token.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK
        )
