from django.test import TestCase
from accounts.models import CustomUser, Employee, Employer, ProfileOption
from accounts.serializers import (
    UserSerializer,
    UserAuthenticationSerializer,
    LoginSerializer,
    ProfileImageUploadSerializer
)
from .test_utils import create_test_image

class UserSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for serializer tests
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.user.save()  # Save to ensure employee_profile is created

    def test_user_serializer_create(self):
        """
        Test creating a user through UserSerializer
        """
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'role': ProfileOption.EMPLOYEE
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.role, ProfileOption.EMPLOYEE)

    def test_user_serializer_update(self):
        """
        Test updating user and profile data
        """
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.email, 'updated@example.com')

class UserAuthenticationSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for authentication serializer tests
        """
        self.user_data = {
            'username': 'authuser',
            'email': 'auth@example.com',
            'password': 'authpassword123',
            'role': ProfileOption.EMPLOYEE
        }

    def test_user_authentication_serializer_create(self):
        """
        Test creating a user through UserAuthenticationSerializer
        """
        serializer = UserAuthenticationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.check_password(self.user_data['password']))

class LoginSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for login serializer tests
        """
        self.user = CustomUser.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='loginpass123'
        )
        self.login_data = {
            'username': 'loginuser',
            'password': 'loginpass123'
        }

    def test_login_serializer_validate_success(self):
        """
        Test successful login validation
        """
        serializer = LoginSerializer(data=self.login_data)
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['user'], self.user)

    def test_login_serializer_validate_failure(self):
        """
        Test login validation with incorrect credentials
        """
        data = {
            'username': 'loginuser',
            'password': 'wrongpass'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class ProfileImageUploadSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for image upload serializer tests
        """
        self.user = CustomUser.objects.create_user(
            username='imageuser',
            email='image@example.com',
            password='imagepass123'
        )
        self.image = create_test_image()

    def test_profile_picture_upload(self):
        """
        Test uploading a profile picture
        """
        data = {
            'image_type': 'profile_picture',
            'image': self.image
        }
        serializer = ProfileImageUploadSerializer(
            instance=self.user,
            data=data,
            context={'request': None}
        )
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)  # Debug line
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertTrue(updated_user.profile_picture)
        self.assertIn('profile_pictures/', str(updated_user.profile_picture))

    def test_profile_banner_upload(self):
        """
        Test uploading a profile banner
        """
        data = {
            'image_type': 'profile_banner',
            'image': self.image
        }
        serializer = ProfileImageUploadSerializer(
            instance=self.user,
            data=data,
            context={'request': None}
        )
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)  # Debug line
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertTrue(updated_user.profile_banner)
        self.assertIn('profile_banners/', str(updated_user.profile_banner))