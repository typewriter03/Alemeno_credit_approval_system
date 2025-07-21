from django.test import TestCase
from core.tasks import ingest_data_task
import tempfile
import pandas as pd
import os

class CeleryIngestionTest(TestCase):
    def test_ingest_data_task(self):
        customer_data = {
            'Customer ID': ['123'],
            'First Name': ['Eve'],
            'Last Name': ['Smith'],
            'Age': [27],
            'Phone Number': ['8888888888'],
            'Monthly Salary': [44444],
            'Approved Limit': [200000]
        }
        loan_data = {
            'Loan ID': ['111'],
            'Customer ID': ['123'],
            'Loan Amount': [44444],
            'Tenure': [12],
            'Interest Rate': [11],
            'Monthly payment': [4000],
            'EMIs paid on Time': [12],
            'Date of Approval': ['2024-01-01'],
            'End Date': ['2025-01-01'],
        }

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as cust_file:
            cust_path = cust_file.name
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as loan_file:
            loan_path = loan_file.name

        pd.DataFrame(customer_data).to_excel(cust_path, index=False)
        pd.DataFrame(loan_data).to_excel(loan_path, index=False)

        result = ingest_data_task(cust_path, loan_path)

        # Clean up temp files
        os.remove(cust_path)
        os.remove(loan_path)

        self.assertIn("Data ingestion complete", result)
