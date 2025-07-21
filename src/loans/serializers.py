from rest_framework import serializers
from .models import Loan

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'start_date', 'end_date']
        read_only_fields = ['loan_id', 'monthly_repayment', 'start_date', 'end_date']

class LoanDetailSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField() # Show customer name instead of ID
    class Meta:
        model = Loan
        fields = '__all__'