import firebase_admin
from firebase_admin import credentials, auth


def initialize_firebase():
    """
    Initializes the Firebase Admin SDK with the provided service account credentials.

    This function sets up the connection to Firebase by loading the credentials from a
    service account key file (firebase-secrets.json).

    """
    try:
        cred = credentials.Certificate("firebase-secrets.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        if not firebase_admin._apps:  # Only log if no app is initialized
            print(f"Failed to initialize Firebase: {e}")

# Only initialize in production environment
if not __debug__:  # This is True when Python is run with -O flag
    initialize_firebase()
