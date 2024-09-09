from .models import Notification
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response




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

class CreateNotification(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        title = input_json.get("title")
        message = input_json.get("message")
        notification_type = input_json.get("notification_type")

        user = request.user
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
        )
        return Response({"Response":notification},status= status.HTTP_200_OK)