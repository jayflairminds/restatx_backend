from rest_framework import serializers
from .models import Project, Loan


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    projectname = serializers.CharField(source="project.projectname", read_only=True)
    address = serializers.CharField(source="project.address", read_only=True)

    class Meta:
        model = Loan
        fields = "__all__"
