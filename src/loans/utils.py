import math
from decimal import Decimal

def calculate_credit_score(customer, loan_history):
    score = 0

    total_emis_paid = sum(loan.emis_paid_on_time for loan in loan_history)
    if total_emis_paid > 10:
        score += 25
    elif total_emis_paid > 5:
        score += 15

    if len(loan_history) > 3:
        score -= 10

    total_loan_amount = sum(loan.loan_amount for loan in loan_history)
    if total_loan_amount > customer.approved_limit * 2:
        score -= 20

    current_emis = sum(loan.monthly_repayment for loan in loan_history if loan.end_date > loan.start_date)
    if current_emis > customer.monthly_salary * Decimal('0.5'):
        score = 0
    return max(0, min(100, score))


def calculate_emi(principal, annual_rate, tenure_months):
    principal = float(principal)
    annual_rate = float(annual_rate)
    tenure_months = float(tenure_months)
    if principal <= 0 or tenure_months <= 0:
        return 0
    monthly_rate = (annual_rate / 100) / 12

    if monthly_rate == 0:
        return round(principal / tenure_months, 2)

    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1

    emi = numerator / denominator
    return round(emi, 2)
