from django.contrib import admin
from construction.models import *
# Register your models here.

@admin.register(Loan)
class Loan(admin.ModelAdmin):
    list_display = ('loanid', 'borrower','lender')

@admin.register(UsesMapping)
class UsesMapping(admin.ModelAdmin):
    list_display = ('id','project_type','uses_type','uses','is_locked')
    list_editable = ('project_type','uses_type','uses','is_locked')