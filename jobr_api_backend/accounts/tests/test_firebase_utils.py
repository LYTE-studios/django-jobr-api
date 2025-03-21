from django.test import TestCase
from unittest.mock import patch, MagicMock
from accounts.firebase_utils import initialize_firebase

class FirebaseUtilsTests(TestCase):
    @patch('firebase_admin.credentials.Certificate')
    @patch('firebase_admin.initialize_app')
    @patch('builtins.open', new_callable=MagicMock)
    def test_initialize_firebase(self, mock_open, mock_initialize_app, mock_certificate):
        """
        Test that Firebase initialization works correctly
        """
        # Create a mock certificate
        mock_cert = MagicMock()
        mock_certificate.return_value = mock_cert
        mock_open.return_value.__enter__.return_value = MagicMock()

        # Call the initialize function
        initialize_firebase()

        # Assert Certificate was called with correct path
        mock_certificate.assert_called_once_with("firebase-secrets.json")
        
        # Assert initialize_app was called with mock certificate
        mock_initialize_app.assert_called_once_with(mock_cert)

    @patch('firebase_admin.credentials.Certificate')
    @patch('firebase_admin.initialize_app')
    def test_initialize_firebase_error(self, mock_initialize_app, mock_certificate):
        """
        Test that Firebase initialization handles errors correctly
        """
        # Make Certificate raise an error
        mock_certificate.side_effect = Exception("Failed to load credentials")

        # Should not raise an exception
        initialize_firebase()

        # Verify that initialize_app was not called
        mock_initialize_app.assert_not_called()