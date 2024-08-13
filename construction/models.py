from django.db import models
from users.models import User

PROJECT_TYPE_CHOICES = [("residential", "Residential"), ("commercial", "Commercial")]

LOAN_STATUS = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("closed", "Closed"),
]


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=50)
    projectname = models.CharField(max_length=50)
    startdate = models.DateTimeField(null=True, blank=True)
    enddate = models.DateTimeField(null=True, blank=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.projectname


class Loan(models.Model):
    loanid = models.AutoField(primary_key=True)
    borrower = models.ForeignKey(
        User, related_name="borrower", on_delete=models.CASCADE
    )
    lender = models.ForeignKey(User, related_name="lender", on_delete=models.CASCADE)
    inspector = models.ForeignKey(
        User, related_name="inspector", on_delete=models.CASCADE
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    loandescription = models.CharField(max_length=200)
    loantype = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=30, decimal_places=5)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    interestrate = models.DecimalField(
        max_digits=18, decimal_places=5, null=True, blank=True
    )
    duration = models.CharField(
        max_length=50, null=True, blank=True
    )  # Added max_length here
    status = models.CharField(max_length=50, choices=LOAN_STATUS)

    def __str__(self):
        return f"Loan {self.loanid}"


class LoanDisbursementSchedule(models.Model):
    loan_disbursment_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    draw_request = models.IntegerField()
    planned_disbursement_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    requested_disbursement_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    date_scheduled = models.DateTimeField(null=True, blank=True)
    date_requested = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    disbursement_status = models.CharField(max_length=200)

    def __str__(self):
        return f"Loan disbursement {self.loan_disbursment_id}"

class Budget(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    concrete = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    steel = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    interior = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    carpentery = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    doors = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    windows = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    glass = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    tiles = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    carpet = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    painting = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    lift = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    garden = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    total = models.DecimalField(max_digits=30, decimal_places=3,null=True)

    def __str__(self):
        return self.id
    
class ContingencyStatus(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    review_months = models.IntegerField()
    cost_to_complete = models.DecimalField(max_digits=30, decimal_places=2,null=True)
    total_direct_cost_budget = models.DecimalField(max_digits=30, decimal_places=2,null=True)

    def __str__(self):
        return self.id

class ScheduleStatus(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    review_months = models.IntegerField()
    deviation_from_schedule_weeks = models.DecimalField(max_digits=30, decimal_places=2,null=True)

    def __str__(self):
        return self.id

class DisbursementSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    theoretical = models.DecimalField(max_digits=30, decimal_places=2,null=True)
    actual = models.DecimalField(max_digits=30, decimal_places=2,null=True)
    review_months = models.IntegerField()

    def __str__(self):
        return self.id

 
class ConstructionStatus(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    milestone = models.CharField(max_length=50)
    percentage_completion = models.DecimalField(max_digits=30, decimal_places=2,null=True)
    review_months = models.IntegerField()

    def __str__(self):
        return self.id    
    
class BudgetMaster(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    project_type = models.CharField(max_length=50,null=True)
    project_total = models.IntegerField(null= True,blank=True)
    loan_budget = models.IntegerField(null= True,blank=True)
    acquisition_loan = models.IntegerField(null= True,blank=True)
    building_loan = models.IntegerField(null= True,blank=True)
    project_loan = models.IntegerField(null= True,blank=True)
    mezzanine_loan = models.IntegerField(null= True,blank=True)
    current_revised_budget = models.IntegerField(null= True,blank=True)
    total_funded = models.IntegerField(null= True,blank=True)
    remaining_to_fund = models.IntegerField(null= True,blank=True)
    total_funded_percentage = models.IntegerField(null= True,blank=True)
    uses = models.CharField(max_length=150)
    uses_type = models.CharField(null=True,blank=True)

    def __str__(self):
        return self.id
    
class DrawTracking(models.Model):
    id = models.AutoField(primary_key=True)
    budget_master = models.ForeignKey(BudgetMaster, on_delete=models.CASCADE)
    draw_request = models.IntegerField()
    planned_disbursement_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    requested_disbursement_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    date_scheduled = models.DateTimeField(null=True, blank=True)
    date_requested = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    disbursement_status = models.CharField(max_length=200)

    def __str__(self):
        return self.id