from rest_framework import generics
from .models import Customer
from .serializers import CustomerSerializer

class RegisterCustomerView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer