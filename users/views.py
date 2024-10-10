from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken,TokenAuthentication
from .serializers import *
from users.models import UserProfile
from rest_framework import generics, status 
from django.core.mail import send_mail 
from django.utils.http import urlsafe_base64_encode 
from django.utils.encoding import force_bytes 
from django.contrib.auth.tokens import default_token_generator 
from django.utils.http import urlsafe_base64_decode
from django.conf import settings
from user_payments.models import Payments



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
        try:
            payment = Payments.objects.get(user=user)
            print('payment',payment)
            subscription_status = payment.subscription_status 
        except Payments.DoesNotExist:
            subscription_status = "inactive"



        return Response(
            {
                "user_data": serialize_user(user),
                "role_type": profile.role_type,
                "token": token,
                 "subscription_status": subscription_status
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

class UserList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        input_params = self.request.query_params

        role_type = input_params.get('role_type')
        if role_type:
            users = UserProfile.objects.filter(role_type = role_type ).order_by('id')
        else:
            users = UserProfile.objects.order_by('id')
        return users
    
class PasswordChange(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password:
            return Response({"error":"old password is required"},status=status.HTTP_400_BAD_REQUEST) 
        
        if not new_password:
            return Response({"error":"new password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({"error":"incorrect old password"},status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save() 

        return Response({"message": "Password changed successfully."},status=status.HTTP_200_OK)
        
class DeleteUser(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def delete(self,request,id):
        
        try:
            user = User.objects.get(id=id)
            if request.user.id == id:
                return Response({"Response":"You cannot delete yourself."},status=status.HTTP_401_UNAUTHORIZED)
            user.delete()
            return Response({"message": f"  User '{user.username}' deleted successfully."}, status=status.HTTP_200_OK) 
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetRequest(APIView):

    def post(self,request):
        username = request.data.get('username') 

        if not username:
            return Response({"error":"username is required"},status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

         # Generate reset token and link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        host = request.get_host()
        # host = 'localhost:5173'
        reset_link = f"{request.scheme}://{host}/reset-password/{uid}/{token}/"
        
        # Send the reset link to the user's email

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response({"message": "Password reset link sent","Email":user.email}, status=status.HTTP_200_OK) 
    
class PasswordResetConfirm(APIView):

    def post(self,request,uidb64, token):

        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password') 

        # Check if the New password is provided
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the confirm password is provided
        if not confirm_password:
            return Response({"error": "Confirm password is required."}, status=status.HTTP_400_BAD_REQUEST) 
        
        # Check if new_password and confirm_password match
        if new_password != confirm_password:
            return Response({"error": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            # Decode uid and get the user
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid user or token"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the token is valid
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST) 
        
        # Set new password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
