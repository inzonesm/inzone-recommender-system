# Firebase to MongoDB Migration Guide

This guide will help you migrate your data from Firebase (Firestore or Realtime Database) to MongoDB.

## Prerequisites

- Python 3.7 or higher
- Firebase project with service account credentials
- MongoDB instance (local or cloud)

## Step-by-Step Instructions

### Step 1: Install Required Packages

Open PowerShell in your project directory and run:

```powershell
pip install -r requirements.txt
```

Or install packages individually:

```powershell
pip install firebase-admin pymongo python-dotenv
```

### Step 2: Get Firebase Service Account Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click on the gear icon (⚙️) → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Download the JSON file and save it as `firebase-credentials.json` in your project directory

### Step 3: Set Up MongoDB

**Option A: Local MongoDB**
1. Install MongoDB from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Start MongoDB service:
   ```powershell
   net start MongoDB
   ```
3. Your connection string will be: `mongodb://localhost:27017/`

**Option B: MongoDB Atlas (Cloud)**
1. Create a free account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Create a database user
4. Get your connection string (it will look like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` file with your actual credentials:
   ```env
   FIREBASE_CRED_PATH=firebase-credentials.json
   FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB_NAME=migrated_database
   ```

### Step 5: Customize the Migration Script

Edit `Migrate_Firebase_to_MongoDB.py` and modify the `main()` function to specify what you want to migrate:

**For Firestore Collections:**
```python
# Migrate specific collections
migrator.migrate_firestore_collection('users')
migrator.migrate_firestore_collection('posts')
migrator.migrate_firestore_collection('comments')

# OR migrate all collections at once
migrator.migrate_all_firestore_collections(exclude_collections=['temp_data'])
```

**For Firebase Realtime Database:**
```python
# Migrate specific paths
migrator.migrate_realtime_db_path('users', 'users')
migrator.migrate_realtime_db_path('products', 'products')
```

### Step 6: Run the Migration

Execute the script:

```powershell
python Migrate_Firebase_to_MongoDB.py
```

### Step 7: Verify the Migration

You can verify the migration using MongoDB Compass or the mongo shell:

**Using MongoDB Compass:**
1. Download from [mongodb.com/products/compass](https://www.mongodb.com/products/compass)
2. Connect using your connection string
3. Browse your collections

**Using mongo shell:**
```powershell
mongosh
use migrated_database
show collections
db.users.findOne()
```

## Migration Features

✓ **Firestore Collections**: Migrates entire collections with all documents
✓ **Realtime Database**: Migrates paths from Firebase Realtime Database
✓ **Timestamp Conversion**: Automatically converts Firebase timestamps to MongoDB datetime
✓ **Document IDs**: Preserves Firebase document IDs as MongoDB `_id`
✓ **Bulk Operations**: Uses efficient bulk insert operations
✓ **Error Handling**: Continues migration even if some documents fail
✓ **Migration Log**: Generates a detailed log file (`migration_log.json`)

## Troubleshooting

### Error: "Cannot resolve import 'firebase_admin'"
**Solution:** Install the required packages:
```powershell
pip install firebase-admin pymongo python-dotenv
```

### Error: "Failed to initialize Firebase"
**Solution:** 
- Check that `firebase-credentials.json` exists and is valid
- Verify the path in your `.env` file
- Ensure `FIREBASE_DATABASE_URL` is correct (if using Realtime Database)

### Error: "MongoDB connection failed"
**Solution:**
- Verify MongoDB is running (local) or connection string is correct (Atlas)
- Check network connectivity
- Verify username/password (for Atlas)
- Whitelist your IP address (for Atlas)

### Error: "No data found"
**Solution:**
- Verify collection/path names are correct
- Check Firebase security rules allow read access
- Ensure your service account has proper permissions

## Migration Log

After migration, check `migration_log.json` for a detailed report of what was migrated:

```json
[
  {
    "source": "Firestore/users",
    "target": "MongoDB/users",
    "count": 150,
    "timestamp": "2025-10-07T10:30:00"
  }
]
```

## Advanced Usage

### Migrating with Custom Transformations

If you need to transform data during migration, modify the migration methods:

```python
# In migrate_firestore_collection method, after doc_dict = doc.to_dict():
doc_dict = self._transform_document(doc_dict)

# Add custom transformation method:
def _transform_document(self, doc: dict) -> dict:
    # Your custom logic here
    if 'email' in doc:
        doc['email'] = doc['email'].lower()
    return doc
```

### Batch Migration with Progress Tracking

For large datasets, you can modify the script to batch process and show progress.

## Security Considerations

⚠️ **Important:**
- **Never commit** `firebase-credentials.json` or `.env` files to version control
- Add these files to `.gitignore`
- Limit service account permissions to read-only if possible
- Use MongoDB authentication in production
- Rotate credentials after migration

## Next Steps

After successful migration:
1. ✓ Verify all data in MongoDB
2. ✓ Test your application with MongoDB
3. ✓ Update application connection strings
4. ✓ Keep Firebase data as backup until fully validated
5. ✓ Implement MongoDB indexes for better performance

## Support

For issues or questions:
- Firebase Admin SDK: [firebase.google.com/docs/admin/setup](https://firebase.google.com/docs/admin/setup)
- PyMongo Documentation: [pymongo.readthedocs.io](https://pymongo.readthedocs.io/)
- MongoDB Atlas: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com/)
