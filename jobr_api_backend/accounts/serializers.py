from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Employee, Employer, UserGallery, ProfileOption, LikedEmployee, Review

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
    class Meta:
        model = Employee
        exclude = ('user',)
        extra_kwargs = {
            field: {'allow_null': True, 'required': False}
            for field in Employee._meta.get_fields() if field.name != 'user'
        }

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        exclude = ('user',)
        extra_kwargs = {
            field: {'allow_null': True, 'required': False}
            for field in Employer._meta.get_fields() if field.name != 'user'
        }

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
    employer_profile = EmployerProfileSerializer(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:
            self.fields['username'].required = False
            self.fields['email'].required = False
            self.fields['role'].required = False
            
            # Profile fields are not required by default, validation will handle requirements
            self.fields['employee_profile'].required = False
            self.fields['employer_profile'].required = False
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
        employer_profile_data = data.get('employer_profile')
        role = self.instance.role if self.instance else data.get('role')

        # For PUT requests, require the correct profile type if no profile exists yet
        if self.context['request'].method == 'PUT':
            if role == ProfileOption.EMPLOYEE:
                if not hasattr(self.instance, 'employee_profile') and not employee_profile_data:
                    raise serializers.ValidationError("Employee profile is required for employee users")
            elif role == ProfileOption.EMPLOYER:
                if not hasattr(self.instance, 'employer_profile') and not employer_profile_data:
                    raise serializers.ValidationError("Employer profile is required for employer users")

        # Remove wrong profile type data silently
        if role == ProfileOption.EMPLOYEE and employer_profile_data:
            data.pop('employer_profile', None)
        elif role == ProfileOption.EMPLOYER and employee_profile_data:
            data.pop('employee_profile', None)

        return data

    def update(self, instance, validated_data):
        # Handle profile updates
        employee_profile_data = validated_data.pop('employee_profile', None)
        employer_profile_data = validated_data.pop('employer_profile', None)

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

        # Update employer profile
        if employer_profile_data and instance.role == ProfileOption.EMPLOYER:
            if not hasattr(instance, 'employer_profile'):
                instance.employer_profile = Employer.objects.create(user=instance)
            for attr, value in employer_profile_data.items():
                setattr(instance.employer_profile, attr, value)
            instance.employer_profile.save()

        return instance

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'profile_picture',
                 'profile_banner', 'sector', 'employee_profile',
                 'employer_profile', 'user_gallery', 'reviews_given',
                 'reviews_received')
        read_only_fields = ('id', 'profile_picture', 'profile_banner')

class EmployeeSerializer(serializers.ModelSerializer):
    profile = EmployeeProfileSerializer(source='*', read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'profile')

class EmployerSerializer(serializers.ModelSerializer):
    profile = EmployerProfileSerializer(source='*', read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employer
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
            'profile_picture': employee_user.profile_picture.url if employee_user.profile_picture else None,
        }

class EmployeeSearchSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    city = serializers.CharField(source='employee_profile.city_name', read_only=True)
    biography = serializers.CharField(source='employee_profile.biography', read_only=True)
    skill = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    function = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'city', 'biography',
                 'skill', 'language', 'function')

    def get_profile_picture(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

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
    profile_picture = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='employer_profile.company_name', read_only=True)
    city = serializers.CharField(source='employer_profile.city', read_only=True)
    biography = serializers.CharField(source='employer_profile.biography', read_only=True)
    website = serializers.URLField(source='employer_profile.website', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'company_name', 'city', 'biography', 'website')

    def get_profile_picture(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

class ProfileImageUploadSerializer(serializers.ModelSerializer):
    image_type = serializers.ChoiceField(choices=['profile_picture', 'profile_banner'])
    image = serializers.ImageField()

    class Meta:
        model = User
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