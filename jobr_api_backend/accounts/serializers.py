from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    CustomUser, Employee, Employer, Review, UserGallery,
    ProfileOption, LikedEmployee
)
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'date_of_birth', 'gender', 'phone_number',
            'city_name', 'biography', 'latitude', 'longitude',
            'phone_session_counts', 'language', 'contract_type',
            'function', 'skill'
        ]

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = [
            'vat_number', 'company_name', 'street_name', 'house_number',
            'city', 'postal_code', 'coordinates', 'website', 'biography'
        ]

class UserGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = ['id', 'gallery']

class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeSerializer(required=False, allow_null=True)
    employer_profile = EmployerSerializer(required=False, allow_null=True)
    user_gallery = UserGallerySerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'profile_picture',
            'profile_banner', 'employee_profile', 'employer_profile',
            'user_gallery'
        ]

    def to_representation(self, instance):
        """
        Handle profile representation based on role
        """
        data = super().to_representation(instance)
        if instance.role == ProfileOption.EMPLOYEE:
            data['employer_profile'] = None
        elif instance.role == ProfileOption.EMPLOYER:
            data['employee_profile'] = None
        return data

    def update(self, instance, validated_data):
        employee_data = validated_data.pop('employee_profile', None)
        employer_data = validated_data.pop('employer_profile', None)

        # Update the user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle profile updates based on role
        if instance.role == ProfileOption.EMPLOYEE:
            # Handle employee profile
            if employee_data is not None:
                if not hasattr(instance, 'employee_profile') or not instance.employee_profile:
                    employee = Employee.objects.create(**employee_data)
                    instance.employee_profile = employee
                else:
                    for attr, value in employee_data.items():
                        setattr(instance.employee_profile, attr, value)
                    instance.employee_profile.save()
            
            # Remove employer profile if it exists
            if hasattr(instance, 'employer_profile') and instance.employer_profile:
                employer = instance.employer_profile
                instance.employer_profile = None
                instance.save()
                employer.delete()

        elif instance.role == ProfileOption.EMPLOYER:
            # Handle employer profile
            if employer_data is not None:
                if not hasattr(instance, 'employer_profile') or not instance.employer_profile:
                    employer = Employer.objects.create(**employer_data)
                    instance.employer_profile = employer
                else:
                    for attr, value in employer_data.items():
                        setattr(instance.employer_profile, attr, value)
                    instance.employer_profile.save()
            
            # Remove employee profile if it exists
            if hasattr(instance, 'employee_profile') and instance.employee_profile:
                employee = instance.employee_profile
                instance.employee_profile = None
                instance.save()
                employee.delete()

        instance.save()
        return instance

class UserAuthenticationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        """
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Properly hash the password
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validate user credentials.
        """
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError("Invalid credentials.")

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class LikedEmployeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = LikedEmployee
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['created_at']

    def get_user(self, obj):
        user = CustomUser.objects.filter(employee_profile=obj.employee).first()
        if user:
            return UserSerializer(user).data
        return None

class EmployeeSearchSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['user']

    def get_user(self, obj):
        user = CustomUser.objects.filter(employee_profile=obj).first()
        if user:
            return UserSerializer(user).data
        return None

class ProfileImageUploadSerializer(serializers.Serializer):
    image_type = serializers.ChoiceField(choices=['profile_picture', 'profile_banner'])
    image = serializers.ImageField(
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
        ]
    )

    def validate_image(self, value):
        """
        Validate image size.
        """
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("The maximum file size that can be uploaded is 5MB")
        return value

    def update(self, instance, validated_data):
        """
        Update user's profile picture or banner.
        """
        image_type = validated_data['image_type']
        image = validated_data['image']

        if image_type == 'profile_picture':
            if instance.profile_picture:
                instance.profile_picture.delete(save=False)
            instance.profile_picture = image
        else:
            if instance.profile_banner:
                instance.profile_banner.delete(save=False)
            instance.profile_banner = image

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Return a representation of the instance.
        """
        image_type = self.validated_data['image_type']
        image_url = instance.profile_picture.url if image_type == 'profile_picture' else instance.profile_banner.url
        return {
            'message': f'{image_type.replace("_", " ").title()} uploaded successfully',
            'image_url': image_url
        }