from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Employee, Employer, Review, UserGallery, ProfileOption
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'profile_picture', 'profile_banner']
        read_only_fields = ['profile_picture', 'profile_banner']

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

class UserGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGallery
        fields = '__all__'

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