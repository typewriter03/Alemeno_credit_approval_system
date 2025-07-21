
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import Loan, Customer
from .serializers import LoanEligibilitySerializer, LoanCreateSerializer, LoanDetailSerializer
from .utils import calculate_credit_score, calculate_emi

class CheckEligibilityView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoanEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = Customer.objects.get(customer_id=data['customer_id'])
        loan_history = Loan.objects.filter(customer=customer)
        
        credit_score = calculate_credit_score(customer, loan_history)

        # Determine interest rate based on credit score
        if credit_score > 50:
            corrected_interest_rate = data['interest_rate']
        elif 50 >= credit_score > 30:
            corrected_interest_rate = max(data['interest_rate'], Decimal('12.0'))
        elif 30 >= credit_score > 10:
            corrected_interest_rate = max(data['interest_rate'], Decimal('16.0'))
        else: # credit_score <= 10
            return Response({"approval": False, "message": "Loan not approved due to low credit score."}, status=status.HTTP_200_OK)
        
        # Final approval check
        total_emis = sum(loan.monthly_repayment for loan in loan_history)
        if data['loan_amount'] + customer.current_debt > customer.approved_limit:
            approval = False
        elif total_emis > customer.monthly_salary * Decimal('0.5'):
            approval = False
        else:
            approval = True

        monthly_installment = calculate_emi(data['loan_amount'], corrected_interest_rate, data['tenure'])

        response_data = {
            "customer_id": customer.customer_id,
            "approval": approval,
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": data['tenure'],
            "monthly_installment": monthly_installment
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CreateLoanView(APIView):
    def post(self, request, *args, **kwargs):
        # We can reuse the eligibility logic or just perform a quick check
        eligibility_response = CheckEligibilityView().post(request._request, *args, **kwargs)

        if not eligibility_response.data.get('approval'):
            return Response({
                "loan_id": None,
                "customer_id": eligibility_response.data.get('customer_id'),
                "loan_approved": False,
                "message": "Loan not approved based on eligibility check.",
                "monthly_installment": None
            }, status=status.HTTP_200_OK)

        # If approved, create the loan
        data = eligibility_response.data
        customer = Customer.objects.get(customer_id=data['customer_id'])
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=request.data.get('loan_amount'),
            tenure=data['tenure'],
            interest_rate=data['corrected_interest_rate'],
            monthly_repayment=data['monthly_installment'],
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30 * data['tenure'])
        )

        # Update customer's current debt
        customer.current_debt += Decimal(request.data.get('loan_amount'))
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Congratulations! Your loan has been approved.",
            "monthly_installment": data['monthly_installment']
        }, status=status.HTTP_201_CREATED)


class ViewLoanView(APIView):
    def get(self, request, loan_id, *args, **kwargs):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            serializer = LoanDetailSerializer(loan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)


class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        loans = Loan.objects.filter(customer__customer_id=customer_id)
        if not loans.exists():
            return Response({"error": "No loans found for this customer"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = LoanDetailSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)