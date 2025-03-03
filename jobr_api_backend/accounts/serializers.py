# accounts/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import (
    CustomUser,
    Employee,
    EmployeeGallery,
    Employer,
    EmployerGallery,
    Admin,
    Review,
    ProfileOption,
)


class EmployeeSerializer(serializers.ModelSerializer):
    # user = UserSerializer(required=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=False
    )

    class Meta:
        model = Employee
        fields = [
            "date_of_birth",
            "gender",
            "phone_number",
            "city_name",
            "biography",
            "user",
            "latitude",
            "longitude",
        ]


class EmployerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=False
    )

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
            "user",
        ]


class AdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), many=False
    )

    class Meta:
        model = Admin
        fields = ["full_name", "user"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        employer_profile = EmployerSerializer(read_only=True)
        employee_profile = EmployeeSerializer(read_only=True)
        admin_profile = AdminSerializer(read_only=True)
        gallery = serializers.SerializerMethodField()

        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "employer_profile",
            "employee_profile",
            "admin_profile",
            "profile_picture",
            "gallery",
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

    def get_gallery(self, obj):
        if obj.role == ProfileOption.EMPLOYEE and obj.employee_profile:
            return EmployeeGallerySerializer(
                obj.employee_profile.employees_gallery.all(), many=True
            ).data
        elif obj.role == ProfileOption.EMPLOYER and obj.employer_profile:
            return EmployerGallerySerializer(
                obj.employer_profile.employers_gallery.all(), many=True
            ).data
        return []

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


class EmployeeGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeGallery
        fields = ["id", "gallery"]


class EmployeeWithGallerySerializer(serializers.ModelSerializer):
    gallery = EmployeeGallerySerializer(many=True, source="employees_gallery")

    class Meta:
        model = Employee
        fields = ["user", "gallery"]


class EmployeeGalleryUpdateSerializer(serializers.Serializer):
    gallery = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False),
        write_only=True,
    )

    def validate(self, data):
        try:
            Employee.objects.get(user=self.context.get("user"))
        except Employee.DoesNotExist:
            raise serializers.ValidationError(
                "Employee with this user ID does not exist."
            )
        gallery = data.get("gallery")
        if not gallery:
            raise serializers.ValidationError("At least one image is required.")
        return data


class EmployerGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerGallery
        fields = ["id", "gallery"]


class EmployerWithGallerySerializer(serializers.ModelSerializer):
    gallery = EmployerGallerySerializer(many=True, source="employers_gallery")

    class Meta:
        model = Employer
        fields = ["user", "gallery"]


class EmployerGalleryUpdateSerializer(serializers.Serializer):
    gallery = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False),
        write_only=True,
    )

    def validate(self, data):
        try:
            Employer.objects.get(user=self.context.get("user"))
        except Employer.DoesNotExist:
            raise serializers.ValidationError(
                "Employer with this user ID does not exist."
            )
        gallery = data.get("gallery")
        if not gallery:
            raise serializers.ValidationError("At least one image is required.")
        return data


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
