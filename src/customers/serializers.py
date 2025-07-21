from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary')
    name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'customer_id', 'name', 'first_name', 'last_name', 'age', 
            'monthly_income', 'approved_limit', 'phone_number'
        ]
        read_only_fields = ['customer_id', 'approved_limit', 'name']
        extra_kwargs = {
            'first_name': {'write_only': True, 'required': True},
            'last_name': {'write_only': True, 'required': True},
        }
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        monthly_salary = validated_data.get('monthly_salary')
        approved_limit = round(36 * monthly_salary / 100000) * 100000
        
        validated_data['approved_limit'] = approved_limit
        return Customer.objects.create(**validated_data)