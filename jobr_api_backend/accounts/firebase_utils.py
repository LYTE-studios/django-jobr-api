import firebase_admin
from firebase_admin import credentials, auth


def initialize_firebase():

    """
    Initializes the Firebase Admin SDK with the provided service account credentials.

    This function sets up the connection to Firebase by loading the credentials from a 
    service account key file (firebase-secrets.json).

    """
    cred = credentials.Certificate("firebase-secrets.json")
    firebase_admin.initialize_app(cred)


initialize_firebase()
