from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken
from .serializers import RegisterSerializer
from users.models import UserProfile


def serialize_user(user):
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


class LoginView(APIView):
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        _, token = AuthToken.objects.create(user)
        profile = UserProfile.objects.get(user=user)
        return Response(
            {
                "user_data": serialize_user(user),
                "role_type": profile.role_type,
                "token": token,
            }
        )


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({"user_info": serialize_user(user), "token": token})


class GetUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
            return Response(
                {
                    "user_data": serialize_user(user),
                    "role_type": profile.role_type,
                }
            )
        except UserProfile.DoesNotExist:
            return Response({"Output": "User profile not found"}, status=400)
