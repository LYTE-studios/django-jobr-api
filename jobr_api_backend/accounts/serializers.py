# accounts/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser, Employee, Employer, Admin


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']  # Include user_type
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user is None:
            raise serializers.ValidationError("Invalid username/password")
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    # user = UserSerializer(required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=False)

    class Meta:
        model = Employee
        fields = ['date_of_birth', 'gender', 'phone_number', 'city_name', 'biography', 'user', 'latitude', 'longitude']


class EmployerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=False)

    class Meta:
        model = Employer
        fields = ['vat_number', 'company_name', 'street_name', 'house_number',
                  'city', 'postal_code', 'coordinates', 'website', 'biography', 'user']


class AdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=False)

    class Meta:
        model = Admin
        fields = ['full_name', 'user']
