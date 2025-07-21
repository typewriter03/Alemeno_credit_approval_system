from celery import shared_task
import pandas as pd
from customers.models import Customer
from loans.models import Loan
from django.utils.dateparse import parse_date
from decimal import Decimal

@shared_task
def ingest_data_task(customer_file_path, loan_file_path):
    try:
        customer_df = pd.read_excel(customer_file_path, engine='openpyxl')
        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['Customer ID'],
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'phone_number': row['Phone Number'],
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                }
            )

        loan_df = pd.read_excel(loan_file_path, engine='openpyxl')
        all_loans_by_customer = {}
        for _, row in loan_df.iterrows():
            customer_id = row['Customer ID']
            if customer_id not in all_loans_by_customer:
                all_loans_by_customer[customer_id] = []
            
            loan_amount = Decimal(row.get('Loan Amount', 0))
            all_loans_by_customer[customer_id].append(loan_amount)
            
            customer = Customer.objects.get(customer_id=customer_id)
            
            start_date_str = str(row['Date of Approval']).split(' ')[0]
            end_date_str = str(row['End Date']).split(' ')[0]

            Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer': customer,
                    'loan_amount': loan_amount,
                    'tenure': row['Tenure'],
                    'interest_rate': row['Interest Rate'],
                    'monthly_repayment': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'start_date': parse_date(start_date_str), # CHANGED
                    'end_date': parse_date(end_date_str),     # CHANGED
                }
            )

        for customer_id, loans in all_loans_by_customer.items():
            customer = Customer.objects.get(customer_id=customer_id)
            customer.current_debt = sum(loans)
            customer.save()

        return "Data ingestion complete! Existing records updated and new records created."
    except FileNotFoundError as e:
        return f"Error: {e}. Make sure the Excel files are in the 'src/' directory."
    except Exception as e:
        return f"An unexpected error occurred: {e}"