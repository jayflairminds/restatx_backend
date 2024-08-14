from django.contrib.auth.models import User
from rest_framework import serializers, validators
from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    role_type = serializers.CharField(max_length=50)

    class Meta:
        model = User

        fields = (
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "role_type",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        User.objects.all(), f"A user with that Email already exists."
                    )
                ],
            },
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        # Save the role_type to the user profile
        UserProfile.objects.create(
            user=user, role_type=validated_data["role_type"].lower()
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"