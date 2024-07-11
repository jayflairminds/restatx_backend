from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import *
from .models import *

class UserProjectsView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Loan.objects.filter(auth_userid=user)
        return Loan.objects.none()
    
# This function needs some editing

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            projects = self.get_queryset()
            project_serializer = ProjectSerializer(projects, many=True)

            loans = Loan.objects.filter()
            loan_serializer = LoanSerializer(loans, many=True)

            # Custom response structure
            custom_response = {
                'user': user.username,
                'role_type': user.role_type,
                'projects': project_serializer.data,
                'loans': loan_serializer.data
            }
            return Response(custom_response)
        return Response({"detail": "Authentication credentials were not provided."}, status=401)