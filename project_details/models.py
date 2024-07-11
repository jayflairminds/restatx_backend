from django.db import models
from users.models import User

PROJECT_TYPE_CHOICES = [
    ("residential", "Residential"),
    ("commercial", "Commercial")
]

LOAN_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('closed', 'Closed'),
]

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=50)
    projectname = models.CharField(max_length=50)
    startdate = models.DateTimeField(null=True, blank=True)
    enddate = models.DateTimeField(null=True, blank=True)
    project_type = models.CharField(
        max_length=50, choices=PROJECT_TYPE_CHOICES
    )

    def __str__(self):
        return self.projectname

class Loan(models.Model):
    loanid = models.AutoField(primary_key=True)
    borrower_id = models.ForeignKey(User, related_name='borrower', on_delete=models.CASCADE)
    lender_id = models.ForeignKey(User, related_name='lender', on_delete=models.CASCADE)
    inspector_id = models.ForeignKey(User, related_name='inspector', on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    loandescription = models.CharField(max_length=200)
    loantype = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=30, decimal_places=5)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    interestrate = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=True)  # Added max_length here
    status = models.CharField(
        max_length=50, choices=LOAN_STATUS
    )

    def __str__(self):
        return f"Loan {self.loanid}"

class LoanDisbursementSchedule(models.Model):  # Corrected class name capitalization
    loan_disbursment_id = models.AutoField(primary_key=True)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE)
    draw_request = models.DecimalField(max_digits=30, decimal_places=5)
    amount = models.DecimalField(max_digits=30, decimal_places=5)
    date_requested = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    disbursement_status = models.CharField(max_length=200)

    def __str__(self):
        return f"Loan disbursement {self.loan_disbursment_id}"
