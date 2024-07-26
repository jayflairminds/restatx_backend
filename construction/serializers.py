from rest_framework import serializers
from .models import *


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    projectname = serializers.CharField(source="project.projectname", read_only=True)
    address = serializers.CharField(source="project.address", read_only=True)
    borrower_name = serializers.CharField(source="borrower.username", read_only=True)
    lender_name = serializers.CharField(source="lender.username", read_only=True)
    inspector_name = serializers.CharField(source="inspector.username", read_only=True)
    class Meta:
        model = Loan
        fields = "__all__"


class LoanDisbursementScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDisbursementSchedule
        fields = "__all__"

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = "__all__"

class ContingencyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContingencyStatus
        fields = "__all__"

class ScheduleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleStatus
        fields = "__all__"

class DisbursementScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisbursementSchedule
        fields = "__all__"

class ConstructionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionStatus
        fields = "__all__"