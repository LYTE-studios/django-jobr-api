from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import (
    CustomUser,
    Employee,
    Admin,
    Company,
    CompanyUser,
    UserGallery,
    ProfileOption,
    LikedEmployee,
    Review
)
from datetime import date
import tempfile
from PIL import Image

class CustomUserModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for CustomUser model tests
        """
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'role': ProfileOption.EMPLOYEE
        }

    def test_create_user(self):
        """
        Test creating a user with valid data
        """
        user = CustomUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, ProfileOption.EMPLOYEE)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """
        Test creating a superuser
        """
        superuser = CustomUser.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpassword123'
        )
        
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_profile_creation(self):
        """
        Test automatic profile creation based on user role
        """
        # Test Employee Profile Creation
        employee_user = CustomUser.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='employeepass',
            role=ProfileOption.EMPLOYEE
        )
        
        self.assertIsNotNone(employee_user.employee_profile)
        self.assertIsInstance(employee_user.employee_profile, Employee)

        # Test Employer Profile Creation
        employer_user = CustomUser.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='employerpass',
            role=ProfileOption.EMPLOYER
        )
        
        self.assertIsNotNone(employer_user.employer_profile)
        self.assertIsInstance(employer_user.employer_profile, Employer)

    def test_user_role_change(self):
        """
        Test changing user role properly handles profiles
        """
        # Create an employee user
        user = CustomUser.objects.create_user(
            username='rolechange',
            email='rolechange@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        
        # Save the employee profile ID
        employee_profile_id = user.employee_profile.id
        
        # Change role to employer
        user.role = ProfileOption.EMPLOYER
        user.save()
        
        # Refresh from db to clear cached relationships
        user.refresh_from_db()
        
        # Verify employee profile was deleted and employer profile was created
        self.assertFalse(Employee.objects.filter(id=employee_profile_id).exists())
        with self.assertRaises(CustomUser.employee_profile.RelatedObjectDoesNotExist):
            user.employee_profile
        self.assertTrue(hasattr(user, 'employer_profile'))
        self.assertIsInstance(user.employer_profile, Employer)
        
        # Save the employer profile ID
        employer_profile_id = user.employer_profile.id
        
        # Change role to admin
        user.role = ProfileOption.ADMIN
        user.save()
        
        # Refresh from db to clear cached relationships
        user.refresh_from_db()
        
        # Verify employer profile was deleted and admin profile was created
        self.assertFalse(Employer.objects.filter(id=employer_profile_id).exists())
        with self.assertRaises(CustomUser.employer_profile.RelatedObjectDoesNotExist):
            user.employer_profile
        self.assertTrue(hasattr(user, 'admin_profile'))
        self.assertIsInstance(user.admin_profile, Admin)

    def test_user_role_change_with_data(self):
        """
        Test changing user role properly handles profile data
        """
        # Create an employee user with profile data
        user = CustomUser.objects.create_user(
            username='datachange',
            email='datachange@example.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        
        # Add data to employee profile
        user.employee_profile.phone_number = '1234567890'
        user.employee_profile.city_name = 'Test City'
        user.employee_profile.save()
        
        # Change role to employer
        user.role = ProfileOption.EMPLOYER
        user.save()
        
        # Refresh from db to clear cached relationships
        user.refresh_from_db()
        
        # Verify employee data is gone and new employer profile is clean
        with self.assertRaises(CustomUser.employee_profile.RelatedObjectDoesNotExist):
            user.employee_profile
        self.assertTrue(hasattr(user, 'employer_profile'))
        self.assertIsNone(user.employer_profile.company_name)
        
        # Add employer data
        user.employer_profile.company_name = 'Test Company'
        user.employer_profile.save()
        
        # Change back to employee
        user.role = ProfileOption.EMPLOYEE
        user.save()
        
        # Refresh from db to clear cached relationships
        user.refresh_from_db()
        
        # Verify employer data is gone and new employee profile is clean
        with self.assertRaises(CustomUser.employer_profile.RelatedObjectDoesNotExist):
            user.employer_profile
        self.assertTrue(hasattr(user, 'employee_profile'))
        self.assertIsNone(user.employee_profile.phone_number)

    def test_profile_picture_upload(self):
        """
        Test profile picture upload functionality
        """
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image = Image.new('RGB', (100, 100), color='red')
            image.save(temp_file.name)
            
            # Create user and upload profile picture
            user = CustomUser.objects.create_user(
                username='picuser', 
                email='pic@example.com', 
                password='picpass'
            )
            
            with open(temp_file.name, 'rb') as pic:
                user.profile_picture = SimpleUploadedFile(
                    name='test_pic.png', 
                    content=pic.read(), 
                    content_type='image/png'
                )
                user.save()
            
            # Verify picture was saved
            self.assertTrue(user.profile_picture)
            self.assertIn('profile_pictures/', str(user.profile_picture))

    def test_profile_banner_upload(self):
        """
        Test profile banner upload functionality
        """
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image = Image.new('RGB', (800, 200), color='blue')
            image.save(temp_file.name)
            
            # Create user and upload profile banner
            user = CustomUser.objects.create_user(
                username='banneruser', 
                email='banner@example.com', 
                password='bannerpass'
            )
            
            with open(temp_file.name, 'rb') as banner:
                user.profile_banner = SimpleUploadedFile(
                    name='test_banner.png', 
                    content=banner.read(), 
                    content_type='image/png'
                )
                user.save()
            
            # Verify banner was saved
            self.assertTrue(user.profile_banner)
            self.assertIn('profile_banners/', str(user.profile_banner))

class EmployeeModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Employee model
        """
        self.user = CustomUser.objects.create_user(
            username='employeetest', 
            email='employee@test.com', 
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee = self.user.employee_profile

    def test_employee_creation(self):
        """
        Test creating an employee profile
        """
        self.employee.date_of_birth = date(1990, 1, 1)
        self.employee.gender = 'male'
        self.employee.phone_number = '1234567890'
        self.employee.save()

        self.assertEqual(str(self.employee), self.user.username)
        self.assertEqual(self.employee.date_of_birth, date(1990, 1, 1))
        self.assertEqual(self.employee.gender, 'male')
        self.assertEqual(self.employee.phone_number, '1234567890')

class EmployerModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for Employer model
        """
        self.user = CustomUser.objects.create_user(
            username='employertest', 
            email='employer@test.com', 
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer = self.user.employer_profile

    def test_employer_creation(self):
        """
        Test creating an employer profile
        """
        self.employer.company_name = 'Test Company'
        self.employer.vat_number = 'BE1234567890'
        self.employer.save()

        self.assertEqual(str(self.employer), self.user.username)
        self.assertEqual(self.employer.company_name, 'Test Company')
        self.assertEqual(self.employer.vat_number, 'BE1234567890')

class UserGalleryModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for UserGallery model
        """
        self.user = CustomUser.objects.create_user(
            username='galleryuser', 
            email='gallery@test.com', 
            password='testpass'
        )

    def test_user_gallery_creation(self):
        """
        Test creating a user gallery entry
        """
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image = Image.new('RGB', (100, 100), color='green')
            image.save(temp_file.name)
            
            with open(temp_file.name, 'rb') as gallery_image:
                gallery_entry = UserGallery.objects.create(
                    user=self.user,
                    gallery=SimpleUploadedFile(
                        name='gallery_test.png', 
                        content=gallery_image.read(), 
                        content_type='image/png'
                    )
                )
            
            self.assertIsNotNone(gallery_entry)
            self.assertEqual(gallery_entry.user, self.user)
            self.assertTrue(gallery_entry.gallery)

class LikedEmployeeModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for LikedEmployee model
        """
        # Create employer user
        self.employer_user = CustomUser.objects.create_user(
            username='employer_test',
            email='employer@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYER
        )
        self.employer = self.employer_user.employer_profile

        # Create employee user
        self.employee_user = CustomUser.objects.create_user(
            username='employee_test',
            email='employee@test.com',
            password='testpass',
            role=ProfileOption.EMPLOYEE
        )
        self.employee = self.employee_user.employee_profile

    def test_liked_employee_creation(self):
        """
        Test creating a liked employee relationship
        """
        liked = LikedEmployee.objects.create(
            employer=self.employer,
            employee=self.employee
        )

        self.assertEqual(str(liked), f"{self.employer} likes {self.employee}")
        self.assertEqual(liked.employer, self.employer)
        self.assertEqual(liked.employee, self.employee)
        self.assertIsNotNone(liked.created_at)

    def test_unique_constraint(self):
        """
        Test that an employer cannot like the same employee twice
        """
        # Create first like
        LikedEmployee.objects.create(
            employer=self.employer,
            employee=self.employee
        )

        # Attempt to create duplicate like
        with self.assertRaises(Exception):
            LikedEmployee.objects.create(
                employer=self.employer,
                employee=self.employee
            )

class ReviewModelTests(TestCase):
    def setUp(self):
        """Set up test data for Review model tests"""
        self.employer = CustomUser.objects.create_user(
            username='employer@test.com',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.employee = CustomUser.objects.create_user(
            username='employee@test.com',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )

    def test_create_review(self):
        """Test creating a review"""
        review = Review.objects.create(
            reviewer=self.employer,
            reviewed=self.employee,
            rating=5,
            comment="Great work!"
        )
        
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great work!")
        self.assertEqual(review.reviewer, self.employer)
        self.assertEqual(review.reviewed, self.employee)
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

    def test_review_validation(self):
        """Test review validation rules"""
        # Test self-review prevention
        with self.assertRaises(ValidationError):
            review = Review(
                reviewer=self.employer,
                reviewed=self.employer,
                rating=5,
                comment="Invalid self review"
            )
            review.clean()

        # Test same role review prevention
        employee2 = CustomUser.objects.create_user(
            username='employee2@test.com',
            email='employee2@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        with self.assertRaises(ValidationError):
            review = Review(
                reviewer=self.employee,
                reviewed=employee2,
                rating=5,
                comment="Invalid same role review"
            )
            review.clean()

    def test_unique_constraint(self):
        """Test that a user can't review the same user twice"""
        Review.objects.create(
            reviewer=self.employer,
            reviewed=self.employee,
            rating=4,
            comment="First review"
        )
        
        with self.assertRaises(Exception):
            Review.objects.create(
                reviewer=self.employer,
                reviewed=self.employee,
                rating=5,
                comment="Duplicate review"
            )

class CompanyModelTests(TestCase):
    def setUp(self):
        """Set up test data for Company model tests"""
        self.employer = CustomUser.objects.create_user(
            username='employer@test.com',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )

    def test_vat_number_inheritance(self):
        """Test that new companies inherit VAT number from the first company"""
        # Get the first company that was automatically created
        first_company = self.employer.companies.first()
        
        # Set a VAT number on the first company
        first_company.vat_number = 'BE0123456789'
        first_company.save()

        # Create a new company using the same flow as the application
        second_company = Company(name="Second Company")
        second_company.save(company_users=[self.employer])
        CompanyUser.objects.create(
            company=second_company,
            user=self.employer,
            role='owner'
        )

        # Verify the second company got the same VAT number
        self.assertEqual(second_company.vat_number, first_company.vat_number)

        # Create a third company using the same flow
        third_company = Company(name="Third Company")
        third_company.save(company_users=[self.employer])
        CompanyUser.objects.create(
            company=third_company,
            user=self.employer,
            role='owner'
        )

        # Verify the third company got the same VAT number
        self.assertEqual(third_company.vat_number, first_company.vat_number)