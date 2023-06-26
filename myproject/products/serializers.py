from rest_framework import serializers
from .models import *

# from django.contrib.auth.models import User
# from rest_framework_simplejwt.tokens import RefreshToken

# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     token = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email', 'token']

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user

#     def get_token(self, obj):
#         refresh = RefreshToken.for_user(obj)
#         return str(refresh.access_token)

# class LoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['email', 'password']


class ProductSearchSerializer(serializers.Serializer):
    category = serializers.CharField(required=False)
    brand = serializers.CharField(required=False)
    min_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    min_quantity = serializers.IntegerField(required=False)
    max_quantity = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(required=False)
    rating = serializers.FloatField(required=False)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'