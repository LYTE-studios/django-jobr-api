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

    """
    Serializer for the Employee model.

    This serializer is used to serialize and deserialize employee-related data.

    Fields:
        - date_of_birth (DateField): The employee's date of birth.
        - gender (CharField): The employee's gender.
        - phone_number (CharField): The employee's contact number.
        - city_name (CharField): The name of the city where the employee resides.
        - biography (TextField): A brief biography of the employee.
        - latitude (FloatField): The latitude coordinate of the employee's location.
        - longitude (FloatField): The longitude coordinate of the employee's location.
    """
    
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

    """
    Serializer for the Employer model.

    This serializer is used to serialize and deserialize employer-related data.

    Fields:
        - vat_number (CharField): The VAT number of the employer's company.
        - company_name (CharField): The name of the company.
        - street_name (CharField): The name of the street where the company is located.
        - house_number (CharField): The house number of the company's address.
        - city (CharField): The city where the company is located.
        - postal_code (CharField): The postal code of the company's address.
        - coordinates (JSONField or CharField): The geographic coordinates of the company.
        - website (URLField): The company's website URL.
        - biography (TextField): A brief biography or description of the company.
    """

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

    """
    Serializer for updating the user's gallery.

    This serializer validates the uploaded images and ensures that the data structure is correct.
    
    Fields:
        - gallery (List[ImageField]): A list of images to be uploaded to the user's gallery.
    
    Validation:
        - Ensures that at least one image is provided.
        - Checks if the user exists based on the provided user ID.
    """

    gallery = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False),
        write_only=True,
    )

    def validate(self, data):

        """
        Validate the uploaded gallery images.

        Args:
            data (dict): The input data containing the user and gallery images.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If no images are provided.
            serializers.ValidationError: If the user ID does not exist.
        """

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

    """
    Serializer for handling user data in the system. This serializer is responsible
    for serializing and deserializing `CustomUser` instances, including related profiles 
    and galleries.

    Attributes:
        employer_profile (EmployerSerializer): Nested serializer for the employer profile.
        employee_profile (EmployeeSerializer): Nested serializer for the employee profile.
        admin_profile (AdminSerializer): Nested serializer for the admin profile.
        user_gallery (UserGallerySerializer): Nested serializer for the user's gallery.

    Methods:
        create(validated_data): Creates a new `CustomUser` instance and sets the password.
        update(instance, validated_data): Updates an existing `CustomUser` instance, handling password updates.
    """

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

        """
        Creates a new `CustomUser` instance and sets the password.

        Args:
            validated_data (dict): The validated data to create a user.

        Returns:
            CustomUser: The newly created `CustomUser` instance.
        """
         
        user = CustomUser(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):

        """
        Updates an existing `CustomUser` instance with the validated data.
        Handles password separately if it's provided.

        Args:
            instance (CustomUser): The existing `CustomUser` instance to update.
            validated_data (dict): The validated data to update the user.

        Returns:
            CustomUser: The updated `CustomUser` instance.
        """

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

    """
    Serializer for creating and validating reviews.

    This serializer is responsible for validating the input data for a review,
    including the reviewer information (employee, employer, or anonymous), 
    rating, and comment.

    Attributes:
        Meta (class): The model and fields used for serializing the review data.
    
    Methods:
        validate(self, attrs): Custom validation to ensure that either an employee 
                                or an anonymous name is provided and the rating is within a valid range.
    
    Responses:
        - ValidationError: If either employee or anonymous name is missing, or if the rating is out of range.
    """

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

        """
        Custom validation to ensure that either an employee or an anonymous name is provided 
        and the rating is within a valid range (1 to 5).

        Args:
            attrs (dict): The validated attributes (review data) before saving.

        Returns:
            attrs (dict): The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails (e.g., missing employee/anonymous name, 
                                          or invalid rating range).
        """
         
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

    """
    Serializer to retrieve employee statistics, including:
    - Number of vacancies applied by the employee.
    - Number of chats sent by the employee.
    - Phone session counts for the employee.

    Attributes:
        vacancies_count (int): The number of vacancies the employee has applied to.
        chats_count (int): The number of chats/messages sent by the employee.
        phone_session_counts (int): The number of phone sessions the employee has participated in.

    Methods:
        get_vacancies_count(self, obj): Returns the number of vacancies the employee has applied for.
        get_chats_count(self, obj): Returns the number of chats/messages sent by the employee.
    """

    vacancies_count = serializers.SerializerMethodField()
    chats_count = serializers.SerializerMethodField()
    phone_session_counts = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ["user", "vacancies_count", "chats_count", "phone_session_counts"]

    def get_vacancies_count(self, obj):

        """
        Retrieves the number of vacancies that the employee has applied for.

        Args:
            obj (Employee): The Employee instance for which the vacancies count is being fetched.

        Returns:
            int: The number of vacancies the employee has applied to.
        """
         
        from vacancies.models import ApplyVacancy

        return ApplyVacancy.objects.filter(employee=obj).count()

    def get_chats_count(self, obj):

        """
        Retrieves the number of chats or messages sent by the employee.

        Args:
            obj (Employee): The Employee instance for which the chats count is being fetched.

        Returns:
            int: The number of chats or messages sent by the employee.
        """
         
        from chat.models import Message

        return Message.objects.filter(sender=obj.user).count()