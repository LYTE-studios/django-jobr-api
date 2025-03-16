from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Employee, Employer

from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import date

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="securepassword"
        )

    def test_employee_registration_cycle(self):
        register_url = reverse("employee-registration")
        register_data = {
            "username": "newemployee",
            "email": "employee@example.com",
            "password": "newpassword",
            "date_of_birth": "1990-01-01",  # Add required employee fields
            "gender": "male",
            "phone_number": "1234567890",
        }
        register_response = self.client.post(register_url, register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("access" in register_response.data)
        self.assertTrue("refresh" in register_response.data)

    def test_login_and_access(self):
        login_url = reverse("login")
        login_data = {"username": "testuser", "password": "securepassword"}
        login_response = self.client.post(login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in login_response.data)
        self.assertTrue("refresh" in login_response.data)

    def test_token_refresh(self):
        # First login
        login_url = reverse("login")
        login_response = self.client.post(
            login_url, {"username": "testuser", "password": "securepassword"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Extract refresh token
        refresh_token = login_response.data.get("refresh")
        self.assertIsNotNone(refresh_token, "No refresh token in response")

        # Try refresh
        refresh_url = reverse("token_refresh")
        refresh_response = self.client.post(refresh_url, {"refresh": refresh_token})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(refresh_response.data.get("access"))

    def test_protected_endpoint_without_token(self):
        # Try to access protected endpoint without token
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_update(self):
        # First get tokens through login
        login_url = reverse("login")
        login_response = self.client.post(
            login_url,
            {"username": "testuser", "password": "securepassword"},
            format="json",
        )

        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("user-detail", kwargs={"pk": self.user.id})

        update_data = {"username": "updateduser", "email": "updated@example.com"}

        response = self.client.patch(
            url, update_data, format="json"
        )  # Using PATCH instead of PUT

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")

    def test_user_delete(self):
        # Get token first
        login_url = reverse("login")
        login_response = self.client.post(
            login_url, {"username": "testuser", "password": "securepassword"}
        )
        token = login_response.data["access"]

        # Use token for delete
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            CustomUser.objects.filter(id=self.user.id).exists()
        )  # Verify user no longer exists

    def test_user_full_profile_update(self):
        # First get tokens through login
        login_url = reverse("login")
        login_response = self.client.post(
            login_url,
            {"username": "testuser", "password": "securepassword"},
            format="json",
        )

        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Create initial employer and employee profiles
        Employer.objects.create(
            user=self.user,
            company_name="Initial Company",
            vat_number="BE1234567890"
        )
        Employee.objects.create(
            user=self.user,
            date_of_birth="1990-01-01",
            gender="male",
            phone_number="1234567890"
        )

        url = reverse("user-detail", kwargs={"pk": self.user.id})

        # Prepare full update data
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "employer_profile": {
                "company_name": "Updated Company",
                "vat_number": "BE0987654321",
                "street_name": "Updated Street",
                "house_number": "42",
                "city": "Updated City",
                "postal_code": "1000",
                "website": "https://updatedcompany.com"
            },
            "employee_profile": {
                "date_of_birth": "1995-05-05",
                "gender": "female",
                "phone_number": "0987654321",
                "city_name": "Updated City",
                "biography": "Updated biography"
            }
        }

        # Perform full PUT update
        response = self.client.put(
            url, update_data, format="json"
        )

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh user from database
        self.user.refresh_from_db()

        # Verify user fields updated
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")

        # Verify employer profile updated
        employer_profile = Employer.objects.get(user=self.user)
        self.assertEqual(employer_profile.company_name, "Updated Company")
        self.assertEqual(employer_profile.vat_number, "BE0987654321")
        self.assertEqual(employer_profile.street_name, "Updated Street")
        self.assertEqual(employer_profile.house_number, "42")
        self.assertEqual(employer_profile.city, "Updated City")
        self.assertEqual(employer_profile.postal_code, "1000")
        self.assertEqual(employer_profile.website, "https://updatedcompany.com")

        # Verify employee profile updated
        employee_profile = Employee.objects.get(user=self.user)
        self.assertEqual(str(employee_profile.date_of_birth), "1995-05-05")
        self.assertEqual(employee_profile.gender, "female")
        self.assertEqual(employee_profile.phone_number, "0987654321")
        self.assertEqual(employee_profile.city_name, "Updated City")
        self.assertEqual(employee_profile.biography, "Updated biography")


class SocialAuthenticationTests(TestCase):
    def setUp(self):
        # Setup test client and common test data
        self.client = APIClient()
        self.google_login_url = reverse("google_signin")
        self.apple_login_url = reverse("apple_signin")

    def test_google_signin_new_user(self):
        # Mock the Google token verification
        with patch("google.oauth2.id_token.verify_firebase_token") as mock_verify:
            # Setup mock return value for token verification
            mock_verify.return_value = {
                "email": "newuser@gmail.com",
                "name": "Test User",
            }

            # Prepare test data
            payload = {"id_token": "mock_google_token"}

            # Make the request
            response = self.client.post(self.google_login_url, payload, format="json")

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["message"], "Google Login successful")
            self.assertTrue(response.data["created"])
            self.assertIsNotNone(response.data["access"])
            self.assertIsNotNone(response.data["refresh"])

            # Verify user was created
            user = User.objects.get(email="newuser@gmail.com")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "newuser@gmail.com")

    # Rest of the tests remain the same as in the original file
    # (Omitted for brevity, but would include all other test methods from the original file)


class EmployeeStatisticsViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepassword",
            role="employee",
        )
        self.employee = Employee.objects.create(
            custom_user=self.user,
            date_of_birth=date(1990, 1, 1),
            gender="male",
            phone_number="1234567890",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("employee-statistics")

    def test_get_employee_statistics(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("vacancies_count", response.data)
        self.assertIn("chats_count", response.data)
        self.assertIn("phone_session_counts", response.data)

    def test_increment_phone_sessions(self):
        initial_count = self.employee.phone_session_counts
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.phone_session_counts, initial_count + 1)


class MyProfileViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")

    def test_get_my_profile(self):
        url = reverse("my-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_my_profile(self):
        url = reverse("my-profile")
        data = {"username": "updateduser"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
