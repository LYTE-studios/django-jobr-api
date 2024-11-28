import firebase_admin
from firebase_admin import credentials, auth

def initialize_firebase():
    cred = credentials.Certificate('jobr-test-5d9e5-firebase-adminsdk-u84ov-3aa06cd2c1.json')
    firebase_admin.initialize_app(cred)

initialize_firebase()