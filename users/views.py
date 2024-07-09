from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken, TokenAuthentication
from .serializers import RegisterSerializer
from users.models import UserProfile 

def serialize_user(user):
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

@api_view(['POST'])
def login(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    _, token = AuthToken.objects.create(user)
    profile = UserProfile.objects.get(user=user)
    return Response({
        'user_data': serialize_user(user),
        'role_type' : profile.role_type,
        'token': token
    })
        

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({
            "user_info": serialize_user(user),
            "token": token
        })


@api_view(['GET'])
def get_user(request):
    user = request.user
    if user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=user)
            return Response({
                'user_data': serialize_user(user),
                'role_type': profile.role_type,
            })
        except UserProfile.DoesNotExist:
            return Response({'Output': 'User profile not found'}, status=400)
    return Response({'Output': 'User is not authenticated'}, status=400)