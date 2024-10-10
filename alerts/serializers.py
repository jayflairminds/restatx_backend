from rest_framework import serializers
from alerts.models import *
from construction.models import *


class NotificationSerializer(serializers.ModelSerializer):
    loandescription = serializers.CharField(source="loan.loandescription", read_only=True)
    loantype = serializers.CharField(source="loan.loantype", read_only=True)
    projectname = serializers.CharField(source="loan.project.projectname", read_only=True)
    amount = serializers.CharField(source="loan.amount", read_only=True)
    start_date = serializers.CharField(source="loan.start_date", read_only=True)
    interestrate = serializers.CharField(source="loan.interestrate", read_only=True)
    duration = serializers.CharField(source="loan.duration", read_only=True)
    status = serializers.CharField(source="loan.status", read_only=True)
    borrower_name = serializers.CharField(source="loan.borrower.username", read_only=True)
    lender_name = serializers.CharField(source="loan.lender.username", read_only=True)
    inspector_name = serializers.CharField(source="loan.inspector.username", read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"