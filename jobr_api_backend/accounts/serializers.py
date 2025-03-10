# accounts/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import (
    CustomUser,
    Employee,
    Employer,
    Admin,
    Review,
    UserGallery,
)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "date_of_birth",
            "gender",
            "phone_number",
            "city_name",
            "biography",
            "latitude",
            "longitude",
        ]


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = [
            "vat_number",
            "company_name",
            "street_name",
            "house_number",
            "city",
            "postal_code",
            "coordinates",
            "website",
            "biography",
        ]


class AdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=False
    )

    class Meta:
        model = Admin
        fields = ["full_name", "user"]


class UserGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = ["id", "gallery"]


class UserGalleryUpdateSerializer(serializers.Serializer):
    gallery = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False),
        write_only=True,
    )

    def validate(self, data):
        try:
            CustomUser.objects.get(user=self.context.get("user"))
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "User with this user ID does not exist."
            )
        gallery = data.get("gallery")
        if not gallery:
            raise serializers.ValidationError("At least one image is required.")
        return data
    
class UserAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = [
            "username",
            "email",
            "password",
            "role",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True,
            },  # Make password optional for updates
            "email": {"required": True},  # Make email optional for updates
            "username": {"required": True},  # Make username optional for updates
            "role": {"required": True},  # Make role optional for updates
        }

class UserSerializer(serializers.ModelSerializer):
    employer_profile = EmployerSerializer(read_only=True)
    employee_profile = EmployeeSerializer(read_only=True)
    admin_profile = AdminSerializer(read_only=True)
    user_gallery = UserGallerySerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "role",
            "employer_profile",
            "employee_profile",
            "admin_profile",
            "profile_picture",
            "user_gallery"
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            },  # Make password optional for updates
            "email": {"required": False},  # Make email optional for updates
            "username": {"required": False},  # Make username optional for updates
            "role": {"required": False},  # Make role optional for updates
        }

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password separately if it's provided
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    attrs["user"] = user
                    return attrs
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Invalid credentials.")
        else:
            raise serializers.ValidationError('Must include "username" and "password".')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "employee",
            "employer",
            "anonymous_name",
            "rating",
            "comment",
            "reviewer_type",
        ]

    def validate(self, attrs):
        # Ensure either employee or anonymous_name is provided
        if not attrs.get("employee") and not attrs.get("anonymous_name"):
            raise serializers.ValidationError(
                "Either an employee or an anonymous name must be provided."
            )

        # Additional validation rules can be added here (e.g., rating range)
        if attrs.get("rating") not in range(1, 6):
            raise serializers.ValidationError("Rating must be between 1 and 5.")

        return attrs


class EmployeeStatisticsSerializer(serializers.ModelSerializer):
    vacancies_count = serializers.SerializerMethodField()
    chats_count = serializers.SerializerMethodField()
    phone_session_counts = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ["user", "vacancies_count", "chats_count", "phone_session_counts"]

    def get_vacancies_count(self, obj):
        from vacancies.models import ApplyVacancy

        return ApplyVacancy.objects.filter(employee=obj).count()

    def get_chats_count(self, obj):
        from chat.models import Message

        return Message.objects.filter(sender=obj.user).count()