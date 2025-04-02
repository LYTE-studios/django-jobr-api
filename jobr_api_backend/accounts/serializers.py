from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate

from .models import Employee, UserGallery, ProfileOption, LikedEmployee, Review, Company, CompanyUser

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

class EmployeeProfileSerializer(serializers.ModelSerializer):
    
    from vacancies.serializers import ContractTypeSerializer, FunctionSerializer, LanguageSerializer, SkillSerializer

    profile_picture_url = serializers.SerializerMethodField()
    profile_banner_url = serializers.SerializerMethodField()
    skill = SkillSerializer(many=True, read_only=True)
    language = LanguageSerializer(many=True, read_only=True)
    function = FunctionSerializer(allow_null=True, read_only=True)
    contract_type = ContractTypeSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Employee
        exclude = ('user', 'profile_picture', 'profile_banner')
        extra_kwargs = {
            field: {'allow_null': True, 'required': False}
            for field in Employee._meta.get_fields()
            if field.name not in ['user', 'profile_picture', 'profile_banner']
        }

    def get_profile_picture_url(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

    def get_profile_banner_url(self, obj):
        return obj.profile_banner.url if obj.profile_banner else None

class CompanySerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    profile_banner_url = serializers.SerializerMethodField()
    sector = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:
            for field in self.fields:
                if field not in self.Meta.read_only_fields:
                    self.fields[field].required = False

    def get_sector(self, obj):
        if obj.sector:
            # Import here to avoid circular import
            from vacancies.serializers import SectorSerializer
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
                 'city', 'postal_code', 'website', 'description',
                'created_at', 'updated_at', 'sector',
                 'profile_picture_url', 'profile_banner_url',)
        read_only_fields = ('created_at', 'updated_at', 'users', 'profile_picture_url', 'profile_banner_url')
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
        }

    def get_profile_picture_url(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

    def get_profile_banner_url(self, obj):
        return obj.profile_banner.url if obj.profile_banner else None

class CompanyUserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CompanyUser
        fields = ('id', 'company', 'user', 'role', 'created_at')
        read_only_fields = ('created_at',)

class UserGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = '__all__'

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
            self.fields['role'].required = False
            
            # Employee profile field is not required by default, validation will handle requirements
            self.fields['employee_profile'].required = False
    user_gallery = UserGallerySerializer(many=True, read_only=True)
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
        # Handle profile updates
        employee_profile_data = validated_data.pop('employee_profile', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update employee profile
        if employee_profile_data and instance.role == ProfileOption.EMPLOYEE:
            if not hasattr(instance, 'employee_profile'):
                instance.employee_profile = Employee.objects.create(user=instance)
            for attr, value in employee_profile_data.items():
                setattr(instance.employee_profile, attr, value)
            instance.employee_profile.save()

        return instance

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'employee_profile',
                 'companies', 'selected_company', 'user_gallery', 'reviews_given',
                 'reviews_received')
        read_only_fields = ('id',)

class EmployeeSerializer(serializers.ModelSerializer):
    profile = EmployeeProfileSerializer(source='*', read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'profile')

class LikedEmployeeSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    user = UserSerializer(source='employee.user', read_only=True)

    class Meta:
        model = LikedEmployee
        fields = ('id', 'employee', 'user', 'created_at')

    def get_employee(self, obj):
        employee_user = obj.employee.user
        return {
            'id': employee_user.id,
            'username': employee_user.username,
            'email': employee_user.email,
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

class VATValidationSerializer(serializers.Serializer):
    vat_number = serializers.CharField(max_length=12)

    def validate_vat_number(self, value):
        if not value:
            raise serializers.ValidationError("VAT number is required")
        return value.upper().strip()