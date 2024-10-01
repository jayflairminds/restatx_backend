from django.db import models
from django.contrib.auth.models import User
from construction.models import *
from django.utils import timezone

class Notification(models.Model):
    ALERT = 'AL'
    INFO = 'IN'
    WARNING = 'WA'
    SUCCESS = 'SU'

    NOTIFICATION_TYPES = [
        (ALERT, 'Alert'),
        (INFO, 'Information'),
        (WARNING, 'Warning'),
        (SUCCESS, 'Success'),
    ]

    notify_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_to',null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_from',null=True)
    notification_type = models.CharField(max_length=2, choices=NOTIFICATION_TYPES, default=INFO)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    link = models.URLField(null=True, blank=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE,null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username} - {self.title}'
