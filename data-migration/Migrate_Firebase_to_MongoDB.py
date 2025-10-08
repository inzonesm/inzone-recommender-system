"""
Firebase to MongoDB Migration Script

This script migrates data from Firebase Realtime Database or Firestore to MongoDB.
Make sure to install required packages and configure credentials before running.

Prerequisites:
1. pip install firebase-admin pymongo python-dotenv
2. Set up Firebase service account credentials
3. Set up MongoDB connection
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import firebase_admin
from firebase_admin import credentials, firestore, db
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseToMongoMigrator:
    """
    Migrates data from Firebase to MongoDB
    """
    
    def __init__(self, firebase_cred_path: str, mongodb_uri: str, mongodb_db_name: str):
        """
        Initialize the migrator with Firebase and MongoDB credentials
        
        Args:
            firebase_cred_path: Path to Firebase service account JSON file
            mongodb_uri: MongoDB connection string
            mongodb_db_name: Target MongoDB database name
        """
        # Initialize Firebase
        try:
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL', '')
            })
            print("✓ Firebase initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing Firebase: {e}")
            raise
        
        # Initialize MongoDB
        try:
            self.mongo_client = MongoClient(mongodb_uri)
            self.mongo_db = self.mongo_client[mongodb_db_name]
            # Test connection
            self.mongo_client.admin.command('ping')
            print("✓ MongoDB connected successfully")
        except Exception as e:
            print(f"✗ Error connecting to MongoDB: {e}")
            raise
        
        self.migration_log = []
    
    def migrate_firestore_collection(self, collection_name: str, target_collection_name: str = None):
        """
        Migrate a Firestore collection to MongoDB
        
        Args:
            collection_name: Name of the Firestore collection
            target_collection_name: Target MongoDB collection name (defaults to collection_name)
        """
        if target_collection_name is None:
            target_collection_name = collection_name
        
        print(f"\n--- Migrating Firestore Collection: {collection_name} ---")
        
        try:
            # Get Firestore collection
            firestore_db = firestore.client()
            docs = firestore_db.collection(collection_name).stream()
            
            # Convert to list of documents
            documents = []
            for doc in docs:
                doc_dict = doc.to_dict()
                doc_dict['_id'] = doc.id  # Use Firestore document ID as MongoDB _id
                
                # Convert timestamps to datetime objects
                doc_dict = self._convert_timestamps(doc_dict)
                documents.append(doc_dict)
            
            if not documents:
                print(f"⚠ No documents found in collection '{collection_name}'")
                return
            
            # Insert into MongoDB
            mongo_collection = self.mongo_db[target_collection_name]
            result = mongo_collection.insert_many(documents, ordered=False)
            
            print(f"✓ Migrated {len(result.inserted_ids)} documents from '{collection_name}' to '{target_collection_name}'")
            
            self.migration_log.append({
                'source': f'Firestore/{collection_name}',
                'target': f'MongoDB/{target_collection_name}',
                'count': len(result.inserted_ids),
                'timestamp': datetime.now()
            })
            
        except BulkWriteError as e:
            print(f"⚠ Partial migration completed with errors: {len(e.details.get('writeErrors', []))} errors")
            print(f"✓ Successfully inserted: {e.details.get('nInserted', 0)} documents")
        except Exception as e:
            print(f"✗ Error migrating collection '{collection_name}': {e}")
            raise
    
    def migrate_realtime_db_path(self, firebase_path: str, target_collection_name: str):
        """
        Migrate data from Firebase Realtime Database to MongoDB
        
        Args:
            firebase_path: Path in Firebase Realtime Database (e.g., 'users')
            target_collection_name: Target MongoDB collection name
        """
        print(f"\n--- Migrating Realtime DB Path: {firebase_path} ---")
        
        try:
            # Get reference to Firebase Realtime Database
            ref = db.reference(firebase_path)
            data = ref.get()
            
            if not data:
                print(f"⚠ No data found at path '{firebase_path}'")
                return
            
            # Convert to list of documents
            documents = []
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        value['_id'] = key
                        documents.append(value)
                    else:
                        documents.append({'_id': key, 'value': value})
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if item is not None:
                        if isinstance(item, dict):
                            item['_id'] = str(i)
                            documents.append(item)
                        else:
                            documents.append({'_id': str(i), 'value': item})
            
            if not documents:
                print(f"⚠ No valid documents to migrate from path '{firebase_path}'")
                return
            
            # Insert into MongoDB
            mongo_collection = self.mongo_db[target_collection_name]
            result = mongo_collection.insert_many(documents, ordered=False)
            
            print(f"✓ Migrated {len(result.inserted_ids)} documents from '{firebase_path}' to '{target_collection_name}'")
            
            self.migration_log.append({
                'source': f'RealtimeDB/{firebase_path}',
                'target': f'MongoDB/{target_collection_name}',
                'count': len(result.inserted_ids),
                'timestamp': datetime.now()
            })
            
        except BulkWriteError as e:
            print(f"⚠ Partial migration completed with errors: {len(e.details.get('writeErrors', []))} errors")
            print(f"✓ Successfully inserted: {e.details.get('nInserted', 0)} documents")
        except Exception as e:
            print(f"✗ Error migrating path '{firebase_path}': {e}")
            raise
    
    def migrate_all_firestore_collections(self, exclude_collections: List[str] = None):
        """
        Migrate all Firestore collections to MongoDB
        
        Args:
            exclude_collections: List of collection names to exclude from migration
        """
        if exclude_collections is None:
            exclude_collections = []
        
        print("\n=== Migrating All Firestore Collections ===")
        
        try:
            firestore_db = firestore.client()
            collections = firestore_db.collections()
            
            for collection in collections:
                if collection.id not in exclude_collections:
                    self.migrate_firestore_collection(collection.id)
                else:
                    print(f"⊘ Skipping collection '{collection.id}' (excluded)")
        
        except Exception as e:
            print(f"✗ Error migrating all collections: {e}")
            raise
    
    def _convert_timestamps(self, data: Any) -> Any:
        """
        Recursively convert Firestore timestamps to Python datetime objects
        
        Args:
            data: Data to convert (dict, list, or primitive)
        
        Returns:
            Converted data
        """
        if isinstance(data, dict):
            return {key: self._convert_timestamps(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_timestamps(item) for item in data]
        elif hasattr(data, 'timestamp'):  # Firestore Timestamp
            return datetime.fromtimestamp(data.timestamp())
        else:
            return data
    
    def export_migration_log(self, output_file: str = 'migration_log.json'):
        """
        Export migration log to a JSON file
        
        Args:
            output_file: Output file path
        """
        log_data = []
        for entry in self.migration_log:
            log_entry = entry.copy()
            log_entry['timestamp'] = log_entry['timestamp'].isoformat()
            log_data.append(log_entry)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Migration log exported to '{output_file}'")
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        total_docs = sum(entry['count'] for entry in self.migration_log)
        
        for entry in self.migration_log:
            print(f"• {entry['source']} → {entry['target']}: {entry['count']} documents")
        
        print(f"\n✓ Total documents migrated: {total_docs}")
        print("="*60)
    
    def close(self):
        """Close database connections"""
        self.mongo_client.close()
        firebase_admin.delete_app(firebase_admin.get_app())
        print("\n✓ Connections closed")


def main():
    """
    Main migration function - Customize this according to your needs
    """
    
    # Configuration
    FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase-credentials.json')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'migrated_database')
    
    print("="*60)
    print("FIREBASE TO MONGODB MIGRATION")
    print("="*60)
    
    try:
        # Initialize migrator
        migrator = FirebaseToMongoMigrator(
            firebase_cred_path=FIREBASE_CRED_PATH,
            mongodb_uri=MONGODB_URI,
            mongodb_db_name=MONGODB_DB_NAME
        )
        
        # Migrate ALL Firestore collections
        migrator.migrate_all_firestore_collections()
        
        # Print summary and export log
        migrator.print_summary()
        migrator.export_migration_log()
        
        # Close connections
        migrator.close()
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
