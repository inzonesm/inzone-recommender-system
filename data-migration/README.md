# Firebase to MongoDB Migration Guide

This guide documents the migration of data from Firebase Firestore to MongoDB Atlas.

## Prerequisites

- Python 3.7 or higher
- Firebase project with service account credentials
- MongoDB Atlas account

## Setup Instructions

### Step 1: Create Conda Environment

Create a new conda environment for this project:

1. Use **Python: Create Environment...** command in VS Code
2. Select **Conda** as environment type
3. Choose Python 3.7 or higher
4. Install dependencies when prompted

Or manually:
```powershell
conda create -n firebase-migration python=3.9
conda activate firebase-migration
pip install -r requirements.txt
```

### Step 2: Get Firebase Service Account Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click on the gear icon (⚙️) → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Download the JSON file and save it as `firebase-credentials.json` in this directory

### Step 3: Set Up MongoDB Atlas

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Select your cluster
3. Click **Connect** button
4. Choose **Connect your application**
5. Copy your connection string (format: `mongodb+srv://username:password@cluster.mongodb.net/`)

**Important:** Make sure to:
- Create a database user with read/write permissions
- Whitelist your IP address in Network Access settings

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` file with your actual credentials:
   ```env
   # Firebase Configuration
   FIREBASE_CRED_PATH=firebase-credentials.json
   FIREBASE_DATABASE_URL=""

   # MongoDB Configuration
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB_NAME=migrated_database
   ```

**Note:** `FIREBASE_DATABASE_URL` can be left empty for Firestore-only migrations.

### Step 5: Customize the Migration Script

Edit `Migrate_Firebase_to_MongoDB.py` to specify your Firestore collections:

```python
def main():
    migrator = FirebaseToMongoMigrator(
        firebase_cred_path=FIREBASE_CRED_PATH,
        mongodb_uri=MONGODB_URI,
        mongodb_db_name=MONGODB_DB_NAME
    )
    
    # Option 1: Migrate all collections
    migrator.migrate_all_firestore_collections()
    
    # Option 2: Migrate specific collections
    # migrator.migrate_firestore_collection('users')
    # migrator.migrate_firestore_collection('posts')
    # migrator.migrate_firestore_collection('products')
    
    migrator.print_summary()
    migrator.export_migration_log()
    migrator.close()
```

### Step 6: Run the Migration

1. Activate your conda environment:
   ```powershell
   conda activate firebase-migration
   ```

2. Execute the migration script:
   ```powershell
   python Migrate_Firebase_to_MongoDB.py
   ```

### Step 7: Verify the Migration

**Using MongoDB Compass:**
1. Download from [mongodb.com/products/compass](https://www.mongodb.com/products/compass)
2. Connect using your MongoDB Atlas connection string
3. Browse your collections and verify data

**Using MongoDB Atlas Web Interface:**
1. Go to your cluster in MongoDB Atlas
2. Click **Browse Collections**
3. Verify all collections and documents are present

## Migration Features

✓ **Firestore Collections**: Migrates all documents from specified collections
✓ **Timestamp Conversion**: Automatically converts Firebase timestamps to MongoDB datetime
✓ **Document IDs**: Preserves Firebase document IDs as MongoDB `_id`
✓ **Bulk Operations**: Uses efficient bulk insert operations (1000 documents per batch)
✓ **Error Handling**: Continues migration even if some documents fail
✓ **Migration Log**: Generates a detailed log file (`migration_log.json`)
✓ **Progress Tracking**: Shows real-time progress for each collection
✓ **Read-Only**: Does NOT modify or delete any data in Firebase

## What Gets Migrated

The script migrates:
- ✅ All documents in each Firestore collection
- ✅ All fields and nested data structures
- ✅ Firebase timestamps (converted to MongoDB datetime)
- ✅ Document IDs (preserved as `_id` in MongoDB)
- ✅ Arrays, objects, and nested collections

## Troubleshooting

### Error: "Cannot resolve import 'firebase_admin'"
**Solution:** Install the required packages:
```powershell
pip install -r requirements.txt
```

### Error: "Failed to initialize Firebase"
**Solution:** 
- Check that `firebase-credentials.json` exists in the correct location
- Verify the JSON file is valid
- Ensure your service account has Firestore read permissions

### Error: "MongoDB connection failed"
**Solution:**
- Verify your connection string is correct
- Check username and password (no angle brackets `<>`)
- Ensure your IP address is whitelisted in MongoDB Atlas Network Access
- Test connection using MongoDB Compass first

### Error: "Authentication failed"
**Solution:**
- Verify MongoDB username and password in `.env` file
- URL encode special characters in password (e.g., `@` → `%40`)
- Check database user has proper permissions in MongoDB Atlas

### No Collections Found
**Solution:**
- Verify your Firestore database has collections
- Check Firebase Console → Firestore Database
- Ensure service account has read permissions

## Migration Log

After migration, check `migration_log.json` for details:

```json
[
  {
    "source": "Firestore/users",
    "target": "MongoDB/users",
    "count": 5332,
    "timestamp": "2025-10-07T20:11:58"
  },
  {
    "source": "Firestore/posts",
    "target": "MongoDB/posts",
    "count": 1387,
    "timestamp": "2025-10-07T20:12:04"
  }
]
```

## Security Considerations

⚠️ **Important:**
- ✅ `firebase-credentials.json` is in `.gitignore` - never commit this file
- ✅ `.env` is in `.gitignore` - never commit credentials
- ✅ `migration_log.json` is in `.gitignore` - may contain sensitive schema info
- ✅ Repository should be set to **Private** on GitHub
- ✅ Rotate credentials after migration is complete
- ✅ The migration script is **read-only** and does NOT modify Firebase data

## Post-Migration Steps

After successful migration:
1. ✓ Verify all collections in MongoDB Atlas
2. ✓ Check document counts match between Firebase and MongoDB
3. ✓ Test your application with MongoDB Atlas connection
4. ✓ Update application to use MongoDB connection string
5. ✓ Keep Firebase data as backup until fully validated
6. ✓ Create indexes in MongoDB for frequently queried fields
7. ✓ Set up MongoDB Atlas backup policies

## Support Resources

- Firebase Admin SDK: [firebase.google.com/docs/admin/setup](https://firebase.google.com/docs/admin/setup)
- PyMongo Documentation: [pymongo.readthedocs.io](https://pymongo.readthedocs.io/)
- MongoDB Atlas Documentation: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com/)
- MongoDB Compass: [mongodb.com/products/compass](https://www.mongodb.com/products/compass)
