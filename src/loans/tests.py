from django.test import TestCase
from decimal import Decimal
from loans.utils import calculate_credit_score, calculate_emi

class DummyLoan:
    def __init__(self, emis_paid_on_time, loan_amount, monthly_repayment, start_date, end_date):
        self.emis_paid_on_time = emis_paid_on_time
        self.loan_amount = loan_amount
        self.monthly_repayment = monthly_repayment
        self.start_date = start_date
        self.end_date = end_date

class DummyCustomer:
    def __init__(self, approved_limit, monthly_salary):
        self.approved_limit = approved_limit
        self.monthly_salary = monthly_salary

class CreditScoreUtilsTest(TestCase):
    def test_calculate_credit_score_typical(self):
        cust = DummyCustomer(approved_limit=200000, monthly_salary=Decimal('50000'))
        from datetime import date, timedelta
        loans = [
            DummyLoan(emis_paid_on_time=12, loan_amount=50000, monthly_repayment=5000,
                      start_date=date.today() - timedelta(days=365),
                      end_date=date.today() + timedelta(days=365))
        ]
        score = calculate_credit_score(cust, loans)
        self.assertTrue(0 <= score <= 100)

    def test_calculate_emi_typical(self):
        emi = calculate_emi(Decimal('120000'), 12, 12)
        self.assertIsInstance(emi, float)
        self.assertGreater(emi, 0)
