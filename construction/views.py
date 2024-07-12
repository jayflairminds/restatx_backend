from rest_framework import generics
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
        print(profile.role_type)
        match profile.role_type:
            case 'lender':
                return Loan.objects.filter(lender_id=user)
            case 'inspector':
                return Loan.objects.filter(inspector_id=user)
            case 'borrower':
                return Loan.objects.filter(borrower_id=user)
