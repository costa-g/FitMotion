import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config.settings import settings
import json

_firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app
    try:
        # Check if already initialized
        _firebase_app = firebase_admin.get_app()
    except ValueError:
        # Initialize Firebase Admin
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app

def get_firebase_app():
    """Get Firebase App instance"""
    global _firebase_app
    if not _firebase_app:
        _firebase_app = initialize_firebase()
    return _firebase_app

def get_firestore_client():
    """Get Firestore client instance"""
    app = get_firebase_app()
    try:
        return firestore.client(app)
    except Exception as e:
        raise Exception(f"Failed to get Firestore client: {str(e)}")