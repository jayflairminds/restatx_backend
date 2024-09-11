from .models import Notification
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import *




def create_notification(notify_to,sender, title, message, notification_type='IN', link=None):

    notification = Notification.objects.create(
        notify_to=notify_to,
        sender = sender,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
    return notification

class NotificationManager(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        input_params = request.query_params
        user = request.user.id
        try:
            notifications = Notification.objects.filter(notify_to=user,is_read=False)
        except Notification.DoesNotExist:
            return Response({"Response":"No Active Notifications exist for the user"},status=status.HTTP_404_NOT_FOUND)
        serializers = NotificationSerializer(notifications,many=True)
        return Response(serializers.data,status= status.HTTP_200_OK)
    
    # def delete():
    #     pass
    
    # def post():
    #     pass