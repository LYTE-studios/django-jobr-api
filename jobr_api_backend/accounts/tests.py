from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser


class UserTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   password='securepassword')

    def test_user_registration(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_user_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'securepassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login successful')

    def test_user_update(self):
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        self.client.login(username='testuser', password='securepassword')
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'password': 'newsecurepassword'  # Note that password is not updated here; modify as necessary
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_user_delete(self):
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        self.client.login(username='testuser', password='securepassword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(id=self.user.id).exists())  # Verify user no longer exists
