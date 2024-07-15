from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from .serializers import *
from .models import *

from .models import Loan
from .serializers import LoanSerializer


class LoanListView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        match profile.role_type:
            case "lender":
                loans = Loan.objects.filter(lender_id=user)
            case "inspector":
                loans = Loan.objects.filter(inspector_id=user)
            case "borrower":
                loans = Loan.objects.filter(borrower_id=user)

        loans = loans.select_related("project")
        return loans

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = response.data

        # Might need to changes this if changes are made in the database structure.
        allowed_keys = {
            "loanid",
            "projectname",
            "address",
            "loandescription",
            "amount",
            "status",
            "loantype",
            "start_date",
            "end_date",
            "interestrate",
            "duration",
            "borrower",
            "lender",
            "inspector",
            "project",
        }

        filtered_data = [
            {key: value for key, value in item.items() if key in allowed_keys}
            for item in data
        ]

        return Response(filtered_data)
