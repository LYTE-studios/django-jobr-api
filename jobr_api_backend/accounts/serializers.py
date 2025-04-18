from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.db import models

from .models import (
    Employee, CompanyGallery, ProfileOption, LikedEmployee, Review,
    Company, CompanyUser, EmployeeGallery
)
from chat.models import ChatRoom
from vacancies.models import ApplyVacancy
from vacancies.models import Sector

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                data["user"] = user
                return data
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        raise serializers.ValidationError("Must include 'email' and 'password'.")

class UserAuthenticationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "role")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user

# Import serializers from vacancies app using absolute imports
from vacancies.serializers import ContractTypeSerializer, FunctionSerializer, LanguageSerializer, SkillSerializer

class EmployeeGallerySerializer(serializers.ModelSerializer):
    gallery_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeGallery
        fields = ('id', 'employee', 'gallery_url')
        read_only_fields = ('gallery_url', 'employee')

    def get_gallery_url(self, obj):
        return obj.gallery.url if obj.gallery else None

    def create(self, validated_data):
        if 'gallery_url' in validated_data:
            gallery_url = validated_data.pop('gallery_url')
            if gallery_url:
                # Extract relative path from full URL
                relative_path = gallery_url.split('/media/')[-1]
                validated_data['gallery'] = relative_path
        return super().create(validated_data)

class EmployeeProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    profile_banner_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    chat_requests = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    skill = SkillSerializer(many=True, read_only=True)
    language = LanguageSerializer(many=True, read_only=True)
    employee_gallery = EmployeeGallerySerializer(many=True, read_only=True)

    def get_chat_requests(self, obj):
        return ChatRoom.objects.filter(
            models.Q(employee=obj.user) | models.Q(employer=obj.user)
        ).count()

    def get_applications(self, obj):
        return ApplyVacancy.objects.filter(employee=obj).count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or request.user.role != ProfileOption.EMPLOYER or not request.user.selected_company:
            return None
        
        return LikedEmployee.objects.filter(
            company=request.user.selected_company,
            employee=obj
        ).exists()
    function = FunctionSerializer(allow_null=True, read_only=True)
    contract_type = ContractTypeSerializer(read_only=True, allow_null=True)
    availability_status = serializers.ChoiceField(
        choices=[
            ('immediately', 'Immediately Available'),
            ('two_weeks', 'Available in 2 Weeks'),
            ('one_month', 'Available in 1 Month'),
            ('three_months', 'Available in 3 Months'),
            ('unavailable', 'Not Available')
        ],
        required=False,
        allow_null=True
    )
    employment_type = serializers.ChoiceField(
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('temporary', 'Temporary'),
            ('internship', 'Internship')
        ],
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        exclude = ('user', 'profile_picture', 'profile_banner')
        # Add is_liked to the fields that will be included in the serialized output
        extra_fields = ('is_liked',)
        extra_kwargs = {
            field: {'allow_null': True, 'required': False}
            for field in Employee._meta.get_fields()
            if field.name not in ['user', 'profile_picture', 'profile_banner']
        }

    def get_profile_picture_url(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

    def get_profile_banner_url(self, obj):
        return obj.profile_banner.url if obj.profile_banner else None

class CompanyGallerySerializer(serializers.ModelSerializer):
    gallery_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyGallery
        fields = ('id', 'company', 'gallery_url')
        read_only_fields = ('gallery_url',)

    def get_gallery_url(self, obj):
        return obj.gallery.url if obj.gallery else None

class CompanyBasicSerializer(serializers.ModelSerializer):
    """Simplified Company serializer for nested relationships."""
    profile_picture_url = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ('id', 'name', 'profile_picture_url', 'street_name', 'house_number',
                 'city', 'postal_code')

    def get_profile_picture_url(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

class CompanySerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    profile_banner_url = serializers.SerializerMethodField()
    sector = serializers.PrimaryKeyRelatedField(
        queryset=Sector.objects.all(),
        required=False,
        allow_null=True
    )
    sector_details = serializers.SerializerMethodField(read_only=True)
    company_gallery = CompanyGallerySerializer(many=True, read_only=True)
    companies = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:
            for field in self.fields:
                if field not in self.Meta.read_only_fields:
                    self.fields[field].required = False

    def get_sector_details(self, obj):
        if obj.sector:
            return {
                'id': obj.sector.id,
                'name': obj.sector.name,
                'enabled': obj.sector.enabled,
                'icon': obj.sector.icon.url if obj.sector.icon else None
            }
        return None

    class Meta:
        model = Company
        fields = ('id', 'name', 'vat_number', 'street_name', 'house_number',
                 'city', 'postal_code', 'website', 'description', 'employee_count',
                'created_at', 'updated_at', 'sector', 'sector_details',
                 'profile_picture_url', 'profile_banner_url', 'company_gallery',
                 'companies')
        read_only_fields = ('created_at', 'updated_at', 'users', 'profile_picture_url', 'profile_banner_url', 'companies')
        extra_kwargs = {
            'name': {'allow_null': True},
            'vat_number': {'allow_null': True},
            'street_name': {'allow_null': True},
            'house_number': {'allow_null': True},
            'city': {'allow_null': True},
            'postal_code': {'allow_null': True},
            'website': {'allow_null': True},
            'description': {'allow_null': True},
            'sector': {'allow_null': True},
            'employee_count': {'allow_null': True},
        }
        
    def get_companies(self, obj):
        """Get all companies associated with the user who owns this company."""
        # Find the owner of this company
        company_user = CompanyUser.objects.filter(company=obj).first()
        if company_user:
            # Get all companies associated with this user
            user_companies = [cu.company for cu in CompanyUser.objects.filter(user=company_user.user)]
            return CompanyBasicSerializer(user_companies, many=True).data
        return []

    def get_profile_picture_url(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

    def get_profile_banner_url(self, obj):
        return obj.profile_banner.url if obj.profile_banner else None

    def update(self, instance, validated_data):
        # Only update fields that are not None
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance

class CompanyUserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CompanyUser
        fields = ('id', 'company', 'user', 'role', 'created_at')
        read_only_fields = ('created_at',)

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewed_username = serializers.CharField(source='reviewed.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'reviewer', 'reviewed', 'reviewer_username', 'reviewed_username',
                 'rating', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        reviewer = data.get('reviewer')
        reviewed = data.get('reviewed')

        if reviewer == reviewed:
            raise serializers.ValidationError("Users cannot review themselves")
        
        if reviewer.role == reviewed.role:
            raise serializers.ValidationError("Users can only review users of different roles")

        # Check if review already exists
        if Review.objects.filter(reviewer=reviewer, reviewed=reviewed).exists():
            raise serializers.ValidationError("You have already reviewed this user")

        return data

class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(required=False, allow_null=True)
    companies = CompanyUserSerializer(source='companyuser_set', many=True, read_only=True)
    selected_company = CompanySerializer(
        required=False,
        allow_null=True,
        read_only=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:
            self.fields['username'].required = False
            self.fields['email'].required = False
            self.fields['first_name'].required = False
            self.fields['last_name'].required = False
            self.fields['role'].required = False
            
            # Employee profile field is not required by default, validation will handle requirements
            self.fields['employee_profile'].required = False
    reviews_given = serializers.SerializerMethodField()
    reviews_received = serializers.SerializerMethodField()

    def get_reviews_given(self, obj):
        reviews = obj.reviews_given.all()
        return ReviewSerializer(reviews, many=True).data

    def get_reviews_received(self, obj):
        reviews = obj.reviews_received.all()
        return ReviewSerializer(reviews, many=True).data

    def validate(self, data):
        # Validate that profile data matches user role
        employee_profile_data = data.get('employee_profile')
        role = self.instance.role if self.instance else data.get('role')

        # For PUT requests, require employee profile if it doesn't exist yet
        if self.context['request'].method == 'PUT':
            if role == ProfileOption.EMPLOYEE:
                if not hasattr(self.instance, 'employee_profile') and not employee_profile_data:
                    raise serializers.ValidationError("Employee profile is required for employee users")

        # Remove employee profile data for non-employee users
        if role != ProfileOption.EMPLOYEE and employee_profile_data:
            data.pop('employee_profile', None)

        # Validate selected_company for employer users
        selected_company = data.get('selected_company')
        if selected_company and self.instance:
            if self.instance.role != ProfileOption.EMPLOYER:
                raise serializers.ValidationError("Only employer users can select a company")
            if not self.instance.companies.filter(id=selected_company.id).exists():
                raise serializers.ValidationError("Selected company must belong to the user")

        return data

    def update(self, instance, validated_data):
        from django.db import transaction

        with transaction.atomic():
            # Handle profile updates
            employee_profile_data = validated_data.pop('employee_profile', None)

            # Update user fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update employee profile
            if employee_profile_data and instance.role == ProfileOption.EMPLOYEE:
                # Get or create employee profile in a transaction-safe way
                employee_profile, _ = Employee.objects.select_for_update().get_or_create(user=instance)
                
                # Handle many-to-many fields separately
                language_data = employee_profile_data.pop('language', None)
                skill_data = employee_profile_data.pop('skill', None)

                # Update regular fields
                for attr, value in employee_profile_data.items():
                    setattr(employee_profile, attr, value)
                employee_profile.save()

                # Update many-to-many fields using set()
                if language_data is not None:
                    employee_profile.language.set(language_data)
                if skill_data is not None:
                    employee_profile.skill.set(skill_data)

                # Handle gallery updates if present in the data
                gallery_data = employee_profile_data.get('employee_gallery')
                if gallery_data is not None:
                    # Get IDs from the request
                    requested_ids = [item.get('id') for item in gallery_data if item.get('id')]
                    
                    # Delete all gallery items not in the request
                    EmployeeGallery.objects.filter(employee=employee_profile).exclude(id__in=requested_ids).delete()
                    
                    # Update existing or create new gallery items
                    for gallery_item in gallery_data:
                        if 'gallery_url' in gallery_item:
                            relative_path = gallery_item['gallery_url'].split('/media/')[-1]
                            if 'id' in gallery_item:
                                # Update existing
                                EmployeeGallery.objects.filter(
                                    id=gallery_item['id'],
                                    employee=employee_profile
                                ).update(gallery=relative_path)
                            else:
                                # Create new
                                EmployeeGallery.objects.create(
                                    employee=employee_profile,
                                    gallery=relative_path
                                )

            # Update company profile for employers
            elif instance.role == ProfileOption.EMPLOYER and instance.selected_company:
                company_data = self.context['request'].data.get('company', {})
                if company_data:
                    company_serializer = CompanySerializer(
                        instance.selected_company,
                        data=company_data,
                        partial=True
                    )
                    company_serializer.is_valid(raise_exception=True)
                    company_serializer.save()

        return instance

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'employee_profile',
                 'companies', 'selected_company', 'reviews_given', 'reviews_received')
        read_only_fields = ('id',)

class EmployeeSerializer(serializers.ModelSerializer):
    profile = EmployeeProfileSerializer(source='*', read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'profile')

class LikedEmployeeSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()

    class Meta:
        model = LikedEmployee
        fields = ('id', 'employee_details', 'created_at')

    def get_employee_details(self, obj):
        if isinstance(obj, dict):
            # Handle dictionary case (during creation)
            return None
        return {
            'id': obj.employee.user.id,
            'username': obj.employee.user.username,
            'email': obj.employee.user.email,
            'profile': {
                'city': obj.employee.city_name,
                'biography': obj.employee.biography,
                'profile_picture_url': obj.employee.profile_picture.url if obj.employee.profile_picture else None,
                'profile_banner_url': obj.employee.profile_banner.url if obj.employee.profile_banner else None
            }
        }

class EmployeeSearchSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='employee_profile.city_name', read_only=True)
    biography = serializers.CharField(source='employee_profile.biography', read_only=True)
    skill = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    function = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    profile_banner_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'city', 'biography',
                 'skill', 'language', 'function', 'profile_picture_url',
                 'profile_banner_url')

    def get_profile_picture_url(self, obj):
        if hasattr(obj, 'employee_profile') and obj.employee_profile:
            return obj.employee_profile.profile_picture.url if obj.employee_profile.profile_picture else None
        return None

    def get_profile_banner_url(self, obj):
        if hasattr(obj, 'employee_profile') and obj.employee_profile:
            return obj.employee_profile.profile_banner.url if obj.employee_profile.profile_banner else None
        return None

    def get_skill(self, obj):
        if hasattr(obj, 'employee_profile') and obj.employee_profile:
            return [{'id': s.id, 'name': s.name} for s in obj.employee_profile.skill.all()]
        return []

    def get_language(self, obj):
        if hasattr(obj, 'employee_profile') and obj.employee_profile:
            return [{'id': l.id, 'name': l.name} for l in obj.employee_profile.language.all()]
        return []

    def get_function(self, obj):
        if hasattr(obj, 'employee_profile') and obj.employee_profile and obj.employee_profile.function:
            return {'id': obj.employee_profile.function.id, 'name': obj.employee_profile.function.name}
        return None

class EmployerSearchSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)
    selected_company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'companies', 'selected_company')

class CompanyImageUploadSerializer(serializers.ModelSerializer):
    image_type = serializers.ChoiceField(choices=['profile_picture', 'profile_banner'])
    image = serializers.ImageField()

    class Meta:
        model = Company
        fields = ('image_type', 'image')

    def update(self, instance, validated_data):
        image_type = validated_data.pop('image_type')
        image = validated_data.pop('image')

        if image_type == 'profile_picture':
            if instance.profile_picture:
                instance.profile_picture.delete()
            instance.profile_picture = image
        else:  # profile_banner
            if instance.profile_banner:
                instance.profile_banner.delete()
            instance.profile_banner = image

        instance.save()
        return instance

class EmployeeImageUploadSerializer(serializers.ModelSerializer):
    image_type = serializers.ChoiceField(choices=['profile_picture', 'profile_banner'])
    image = serializers.ImageField()

    class Meta:
        model = Employee
        fields = ('image_type', 'image')

    def update(self, instance, validated_data):
        image_type = validated_data.pop('image_type')
        image = validated_data.pop('image')

        if image_type == 'profile_picture':
            if instance.profile_picture:
                instance.profile_picture.delete()
            instance.profile_picture = image
        else:  # profile_banner
            if instance.profile_banner:
                instance.profile_banner.delete()
            instance.profile_banner = image

        instance.save()
        return instance

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewed_username = serializers.CharField(source='reviewed.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'reviewer', 'reviewed', 'reviewer_username', 'reviewed_username',
                 'rating', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        reviewer = data.get('reviewer')
        reviewed = data.get('reviewed')

        if reviewer == reviewed:
            raise serializers.ValidationError("Users cannot review themselves")
        
        if reviewer.role == reviewed.role:
            raise serializers.ValidationError("Users can only review users of different roles")

        # Check if review already exists
        if Review.objects.filter(reviewer=reviewer, reviewed=reviewed).exists():
            raise serializers.ValidationError("You have already reviewed this user")

        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_new_password(self, value):
        # Add password validation here if needed
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

class VATValidationSerializer(serializers.Serializer):
    vat_number = serializers.CharField(max_length=12)

    def validate_vat_number(self, value):
        if not value:
            raise serializers.ValidationError("VAT number is required")
        return value.upper().strip()