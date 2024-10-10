from .models import *
from .serializers import *
from django.db.models import Max,Sum
import numpy as np

def disbursement_schedule(loan_id):
    loan_obj = Loan.objects.get(pk=loan_id)
    duration = int(loan_obj.duration)
    total_loan_budget = BudgetMaster.objects.filter(loan_id= loan_id).aggregate(total_loan_budget= Sum('loan_budget'))
    draws_obj_lis = DrawTracking.objects.filter(loan_id=loan_id).values('draw_request','total_released_amount')
    if len(draws_obj_lis) > duration:
        duration = len(draws_obj_lis)

    months = np.arange(0, duration) # Dividing total months into list of months
    normalized_months = (months - duration / 2) / (duration / 10)

    s_curve_values = sigmoid(normalized_months)
    print("total_loan_budget",total_loan_budget['total_loan_budget'])
    scaled_s_curve_values = s_curve_values * total_loan_budget['total_loan_budget']
    
    draw_request_dict = {item['draw_request']: item['total_released_amount'] for item in draws_obj_lis}
    print('draw_request_dict',draw_request_dict)
    output_lis = create_disbursement_schedule_output_json(months, scaled_s_curve_values, draw_request_dict)
    return output_lis

def sigmoid(amount):
    return 1 / (1 + np.exp(-amount))

def create_disbursement_schedule_output_json(months,scaled_s_curve_values,draw_request_dict):
    input_lis = list(zip(months, scaled_s_curve_values))
    print(input_lis)
    output_lis = list()
    for i,j in input_lis: 
        print(i,j)
        output_dictionary = {
            "theoretical": j,
            "review_month":i
        }
         # If draw_request (from DrawTracking) matches the review_month
        if i in draw_request_dict:
            output_dictionary["actual"] = draw_request_dict[i]  # Add actual key with total_released
        else:
            output_dictionary["actual"] = 0
        output_lis.append(output_dictionary)
    return output_lis


def construction_expenditure(loan_id):
    budget_master_lis = BudgetMaster.objects.filter(loan_id=loan_id).values_list('id','uses')
    budget_master_ids = [i[0] for i in budget_master_lis]
    max_draw = DrawRequest.objects.filter(budget_master__in = budget_master_ids).aggregate(Max('draw_request'))
    draw_request = DrawRequest.objects.filter(budget_master__in = budget_master_ids,draw_request=max_draw['draw_request__max'])
    expenditure_lis =  list()
    for draw in draw_request:
        for id,uses in budget_master_lis:
            if draw.budget_master_id == id:
                expenditure_dict = dict()
                expenditure_dict['released_amount'] = draw.released_amount
                expenditure_dict['uses'] = uses
                expenditure_lis.append(expenditure_dict)
    return expenditure_lis