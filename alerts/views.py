from .models import Notification
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




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
        page = input_params.get('page', 1)  
        n_records = input_params.get('n_records', 5)  # Default records per page to 5 if not provided
        user = request.user.id
        
        try:
            notifications = Notification.objects.filter(notify_to=user, is_read=False).order_by('-created_at')
        except Notification.DoesNotExist:
            return Response({"Response": "No Active Notifications exist for the user"}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = Paginator(notifications, n_records)
        
        try:
            paginated_notifications = paginator.page(page)
        except PageNotAnInteger:
            paginated_notifications = paginator.page(1)
        except EmptyPage:
            paginated_notifications = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page
        
        serializers = NotificationSerializer(paginated_notifications, many=True)
        
        return Response({
            "notifications": serializers.data,
            "current_page": paginated_notifications.number,
            "total_pages": paginator.num_pages,
            "total_notifications": paginator.count,
        }, status=status.HTTP_200_OK)
    
    # def delete():
    #     pass
    
    def post(self,request):
        input_json = request.data
        notification_id = input_json['notification_id']
        try:
            notification_instance = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            return Response({'Response':'Specified Notification does not exist'},status=status.HTTP_404_NOT_FOUND)
        
        notification_instance.is_read = True
        notification_instance.save()
        return Response({'Response':'Notification has been Read'},status=status.HTTP_200_OK)