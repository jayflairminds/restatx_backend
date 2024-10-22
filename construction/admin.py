from django.contrib import admin
from construction.models import *
# Register your models here.

@admin.register(Loan)
class Loan(admin.ModelAdmin):
    list_display = ('loanid', 'borrower', 'inspector','lender')