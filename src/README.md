# Credit Approval System by Abhay Sharma

As per the assignment given to me by Alemeno 
A Django-based backend system for managing customer and loan data, including credit approval logic, REST APIs, background data ingestion using Celery, and Docker support.
The Whole System is Unit Teested and adjusted according to handle various error and situations

## Table of Contents
- Features
- Project Structure
- Setup & Installation
- Configuration
- Core Functionality
- API Endpoints
- Celery Tasks
- Docker Usage
- Testing
- Example Unit Tests (Credit Logic)
- Contributing

## Features
- Customer and loan management
- Credit approval logic based on custom rules
- RESTful API endpoints for customer and loan operations
- Background data ingestion from Excel files using Celery
- PostgreSQL database support
- Docker-ready setup

## Project Structure
```
src/
├── core/
│   ├── tasks.py                 # Celery tasks for data ingestion
│   └── management/commands/     # Custom Django management commands
│   └── tests.py                 # Core (Celery/data ingestion) tests
├── customers/
│   ├── models.py                # Customer model
│   ├── serializers.py           # DRF serializers for Customer
│   ├── views.py                 # API views for Customer
│   ├── urls.py                  # Customer API routes
│   └── tests.py                 # Customer API and model tests
├── loans/
│   ├── models.py                # Loan model
│   ├── serializers.py           # DRF serializers for Loan
│   ├── views.py                 # API views for Loan
│   ├── utils.py                 # Credit score & EMI calculation
│   ├── urls.py                  # Loan API routes
│   └── tests.py                 # Loan model, credit logic, and utility tests
├── credit_approval_system/
│   ├── settings.py              # Django settings
│   ├── test_settings.py         # Alternate settings for testing (SQLite)
│   ├── urls.py                  # Project URL configuration
│   ├── celery.py                # Celery app configuration
│   └── wsgi.py, asgi.py         # WSGI/ASGI entry points
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker build file
├── customer_data.xlsx           # Sample customer data
├── loan_data.xlsx               # Sample loan data
```

## Setup & Installation
1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables** (for PostgreSQL connection)
4. **Run migrations**
   ```bash
   python manage.py migrate
   ```
5. **Start the development server**
   ```bash
   python manage.py runserver
   ```
6. **Start Celery worker**
   ```bash
   celery -A credit_approval_system worker --loglevel=info
   ```

## Configuration
- Database settings are in `settings.py` (use environment variables).
- For unit/integration testing, use `test_settings.py` to enable lightweight SQLite in-memory DB:
    ```
    python manage.py test --settings=credit_approval_system.test_settings
    ```
---

## Core Functionality

### Customers
- Model: Stores customer details, salary, approved limit, and current debt.
- Serializer: Handles input/output validation and remaps fields for API.
- API: Register new customers, view customer details.

### Loans
- Model: Stores loan details, repayment info, and links to customers.
- Serializer: Handles loan creation and detail views.
- API: Check loan eligibility, create loans, view loans.

### Credit Approval Logic
- Implemented in `loans/utils.py`:
  - Calculates credit score based on loan history, EMIs, and salary.
  - Calculates EMI for loan offers.

### Data Ingestion
- Celery task in `core/tasks.py`:
  - Reads customer and loan data from Excel files.
  - Updates or creates records in the database.
  - Recalculates customer debt.
- Triggered via Django management command:
  ```bash
  python manage.py ingest_data
  ```

## API Endpoints
- `/api/check-eligibility/` — Check loan eligibility for a customer
- `/api/create-loan/` — Create a new loan
- `/api/view-loan//` — View loan details
- `/api/view-loans//` — View all loans for a customer
- `/api/customers/` — Register and view customers

## Celery Tasks
- `ingest_data_task`: Ingests customer and loan data from Excel files asynchronously.

## Docker Usage
- The project supports Docker for easy deployment.
- Use your provided `Dockerfile` and `docker-compose.yml` to run Django, Celery, PostgreSQL, and Redis services together.
- Example command:
   ```bash
   docker-compose up --build
   ```
- Access Django at [http://localhost:8000](http://localhost:8000)
- Celery worker runs in the background for async tasks

## Testing

- The project uses Django’s built-in test runner for all tests, including model, API, background task, and business logic.
- Tests for different modules are located in each app’s `tests.py`.
- For most unit testing, use the SQLite-based `test_settings.py`:
  ```bash
  python manage.py test --settings=credit_approval_system.test_settings
  ```

## Example Unit Tests: Credit Scoring and EMI Logic

Basic unit tests for your loan scoring and EMI calculations are included in `src/loans/tests.py`.  
They use dummy in-memory objects to verify logic without needing database objects:

```python
# src/loans/tests.py

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
        from datetime import date, timedelta
        cust = DummyCustomer(approved_limit=200000, monthly_salary=Decimal('50000'))
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
```
- These tests ensure the credit logic always returns valid scores and EMIs.
- You can extend with edge-case or negative scenario tests as needed.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

**For further customization or advanced test scenarios, add new test cases in the respective `tests.py` files inside each Django app directory.**

Thank You for Reading 
Abhay Sharma