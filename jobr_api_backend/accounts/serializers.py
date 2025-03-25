from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Employee, Employer, UserGallery, ProfileOption, LikedEmployee

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

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        exclude = ('user',)

class UserGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(read_only=True)
    employer_profile = EmployerProfileSerializer(read_only=True)
    user_gallery = UserGallerySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'profile_picture',
                 'profile_banner', 'sector', 'employee_profile',
                 'employer_profile', 'user_gallery')
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

class VATValidationSerializer(serializers.Serializer):
    vat_number = serializers.CharField(max_length=12)

    def validate_vat_number(self, value):
        if not value:
            raise serializers.ValidationError("VAT number is required")
        return value.upper().strip()