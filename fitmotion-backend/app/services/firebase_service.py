from firebase_admin import firestore, auth
from google.cloud.firestore import Client
from google.cloud.firestore import SERVER_TIMESTAMP
from fastapi import HTTPException
from app.core.config.firebase import get_firebase_app, get_firestore_client

class FirebaseService:
    def __init__(self):
        try:
            get_firebase_app()  # Ensure Firebase is initialized
            self.db: Client = get_firestore_client()
            self.auth = auth
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Firebase service: {str(e)}"
            )
    
    def timestamp(self):
        """Return server timestamp"""
        return SERVER_TIMESTAMP

    async def get_document(self, collection: str, document_id: str) -> dict:
        """Get a document from Firestore"""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get document: {str(e)}"
            )

    async def set_document(self, collection: str, document_id: str, data: dict) -> None:
        """Set a document in Firestore"""
        try:
            self.db.collection(collection).document(document_id).set(data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set document: {str(e)}"
            )

    async def update_document(self, collection: str, document_id: str, data: dict) -> None:
        """Update a document in Firestore"""
        try:
            self.db.collection(collection).document(document_id).update(data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update document: {str(e)}"
            )

    async def delete_document(self, collection: str, document_id: str) -> None:
        """Delete a document from Firestore"""
        try:
            self.db.collection(collection).document(document_id).delete()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document: {str(e)}"
            )

    async def query_collection(self, collection: str, filters: list = None, order_by: tuple = None, limit: int = None):
        """Query a collection with filters"""
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            
            if order_by:
                field, direction = order_by
                query = query.order_by(field, direction=direction)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query collection: {str(e)}"
            )

    async def batch_write(self, operations: list) -> None:
        """Perform batch write operations"""
        try:
            batch = self.db.batch()
            
            for op in operations:
                if op['type'] == 'set':
                    ref = self.db.collection(op['collection']).document(op['document_id'])
                    batch.set(ref, op['data'])
                elif op['type'] == 'update':
                    ref = self.db.collection(op['collection']).document(op['document_id'])
                    batch.update(ref, op['data'])
                elif op['type'] == 'delete':
                    ref = self.db.collection(op['collection']).document(op['document_id'])
                    batch.delete(ref)
            
            batch.commit()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to perform batch operation: {str(e)}"
            )

    async def verify_id_token(self, id_token: str) -> dict:
        """Verify Firebase ID token"""
        try:
            return self.auth.verify_id_token(id_token)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )

    async def get_user_by_email(self, email: str):
        """Get user by email"""
        try:
            return self.auth.get_user_by_email(email)
        except self.auth.UserNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user: {str(e)}"
            )