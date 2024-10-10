from django.db import models
from users.models import User
from django.db.models import Sum

PROJECT_TYPE_CHOICES = [("residential", "Residential"), ("commercial", "Commercial")]

LOAN_STATUS = [
    ("Pending", "pending"),
    ("Approved", "approved"),
    ("Closed", "closed"),
]


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=50)
    projectname = models.CharField(max_length=50)
    street_address = models.CharField(max_length=50,null=True)
    zip_Code = models.CharField(max_length=50,null=True)
    city = models.CharField(max_length=50,null=True)
    lot = models.CharField(max_length=50,null=True)
    block = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50,null=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.projectname


class Loan(models.Model):
    loanid = models.AutoField(primary_key=True)
    borrower = models.ForeignKey(
        User, related_name="borrower", on_delete=models.CASCADE
    )
    lender = models.ForeignKey(User, related_name="lender", on_delete=models.SET_NULL, null = True)
    inspector = models.ForeignKey(
        User, related_name="inspector", on_delete=models.SET_NULL, null = True
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
    original_loan_budget = models.IntegerField(null= True,blank=True,default=0)
    adjustments = models.IntegerField(null=True,blank=True,default=0)
    revised_budget = models.IntegerField(null= True,blank=True,default=0)
    equity_budget = models.IntegerField(null=True,blank=True,default=0)
    loan_budget = models.IntegerField(null=True,blank=True,default=0)
    acquisition_loan = models.IntegerField(null= True,blank=True,default=0)
    building_loan = models.IntegerField(null= True,blank=True,default=0)
    project_loan = models.IntegerField(null= True,blank=True,default=0)
    mezzanine_loan = models.IntegerField(null= True,blank=True,default=0)
    total_funded = models.IntegerField(null= True,blank=True,default=0)
    remaining_to_fund = models.IntegerField(null= True,blank=True,default=0)
    total_funded_percentage = models.IntegerField(null= True,blank=True,default=0)
    uses = models.CharField(max_length=150)
    uses_type = models.CharField(null=True,blank=True)

    def __str__(self):
        return f"BudgetMaster ID {self.id}"
    
class DrawTracking(models.Model):
    id = models.AutoField(primary_key=True)
    draw_request = models.IntegerField()
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE,null=True)
    total_released_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    total_budget_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    total_funded_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True,default=0)
    total_balance_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    total_draw_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    requested_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    draw_status = models.CharField(max_length=200)

    def __str__(self):
        return f"Draw Tracking ID {self.id}"

    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        # Update the remaining_to_fund in the related BudgetMaster
        self.update_budget_master()

    def get_budget_master(self):
        # Retrieve BudgetMaster related to this DrawTracking's loan
        return BudgetMaster.objects.filter(loan=self.loan).all()

    def update_budget_master(self):

        budget_master = self.get_budget_master()
        update_budget_lis = list()
        for budget in budget_master:
            # Sum up total funded amounts from all related DrawTracking instances
            total_funded = DrawRequest.objects.filter(budget_master=budget.id).aggregate(
                total_funded=Sum('funded_amount')
            )['total_funded'] or 0  # Default to 0 if no DrawTracking exists
            # Update the BudgetMaster's total_funded and remaining_to_fund
            budget.total_funded = total_funded
            budget.remaining_to_fund = budget.loan_budget - total_funded
            budget.total_funded_percentage = (total_funded / budget.loan_budget)*100 if budget.loan_budget !=0 else 0
            update_budget_lis.append(budget)
        BudgetMaster.objects.bulk_update(update_budget_lis, ['total_funded', 'remaining_to_fund', 'total_funded_percentage'])    
    
class DrawRequest(models.Model):
    id = models.AutoField(primary_key=True)
    budget_master = models.ForeignKey(BudgetMaster, on_delete=models.CASCADE)
    draw_request = models.IntegerField()
    released_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    budget_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    funded_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    balance_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    draw_amount = models.DecimalField(max_digits=30, decimal_places=3,null=True)
    description = models.CharField(max_length=200,null=True)
    invoice = models.CharField(max_length=100,null=True)
    requested_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Draw Request ID {self.id}"