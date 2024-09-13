from .models import *
from .serializers import *
from django.db.models import Max,Sum
import numpy as np

def disbursement_schedule(loan_id):
    loan_obj = Loan.objects.get(pk=loan_id)
    duration = int(loan_obj.duration)
    total_loan_budget = BudgetMaster.objects.filter(loan_id= loan_id).aggregate(total_loan_budget= Sum('loan_budget'))

    months = np.arange(1, duration + 1) # Dividing total months into list of months
    normalized_months = (months - duration / 2) / (duration / 10)

    s_curve_values = sigmoid(normalized_months)
    print("total_loan_budget",total_loan_budget['total_loan_budget'])
    scaled_s_curve_values = s_curve_values * total_loan_budget['total_loan_budget']
    output_lis = create_output_json(months,scaled_s_curve_values)
    return output_lis

def sigmoid(amount):
    return 1 / (1 + np.exp(-amount))

def create_output_json(months,scaled_s_curve_values):
    input_lis = list(zip(months, scaled_s_curve_values))
    print(input_lis)
    output_lis = list()
    for i,j in input_lis: 
        print(i,j)
        output_dictionary = {
            "theoretical": j,
            "month":i
        }
        output_lis.append(output_dictionary)
    return output_lis
