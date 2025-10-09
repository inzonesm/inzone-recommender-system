# Firestore to Gorse Sync Script

This script syncs your Firestore data (users, items, interactions) to the Gorse recommendation engine.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Gorse is running:**
   ```bash
   docker ps  # Should show gorse_mongo, gorse_master, gorse_server, gorse_worker
   ```

## Customize for Your Firestore Structure

You need to modify the script based on your actual Firestore collections and fields:

### 1. Users Collection
In `fetch_users_from_firestore()`, update:
- **Collection name**: Replace `'users'` with your collection name
- **Fields**: Map your Firestore fields to Gorse user properties

Example Firestore user document:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "interests": ["sports", "tech"],
  "age_group": "25-34"
}
```

Map to Gorse:
```python
user = {
    "UserId": doc.id,
    "Labels": user_data.get('interests', []) + [user_data.get('age_group', '')],
    "Comment": user_data.get('name', '')
}
```

### 2. Items Collection
In `fetch_items_from_firestore()`, update:
- **Collection name**: Replace `'posts'` with your collection (e.g., `'products'`, `'articles'`, `'videos'`)
- **Fields**: Map your item properties

Example Firestore item document:
```json
{
  "title": "Great Article",
  "categories": ["technology", "ai"],
  "tags": ["machine-learning", "python"],
  "created_at": "2025-01-15T10:00:00",
  "is_published": true
}
```

Map to Gorse:
```python
item = {
    "ItemId": doc.id,
    "IsHidden": not item_data.get('is_published', True),
    "Categories": item_data.get('categories', []),
    "Labels": item_data.get('tags', []),
    "Comment": item_data.get('title', '')
}
```

### 3. Interactions/Feedback Collection
In `fetch_interactions_from_firestore()`, update:
- **Collection name**: Your interactions collection (e.g., `'likes'`, `'views'`, `'engagements'`)
- **Feedback types**: Based on your config.toml:
  - Positive: `like`, `share`, `comment`
  - Read: `read`, `view`

Example Firestore interaction document:
```json
{
  "user_id": "user123",
  "post_id": "post456",
  "type": "like",
  "timestamp": "2025-01-15T12:30:00"
}
```

## Run the Script

```bash
python sync_firestore_to_gorse.py
```

## Expected Output

```
============================================================
Starting Firestore to Gorse Sync
============================================================

[1/3] Syncing Users...
Fetched 150 users from Firestore
✓ Batch inserted 150 users

[2/3] Syncing Items...
Fetched 500 items from Firestore
✓ Batch inserted 500 items

[3/3] Syncing Interactions...
Fetched 2500 interactions from Firestore
✓ Batch inserted 100 interactions
✓ Batch inserted 100 interactions
...

============================================================
Sync completed!
============================================================
Total Users: 150
Total Items: 500
Total Interactions: 2500

You can now access recommendations via:
  - Dashboard: http://localhost:8088
  - API: http://localhost:8087/api/recommend/{user_id}?n=10
```

## Testing Recommendations

After syncing, test the API:

```bash
# Get recommendations for a user
curl -H "X-API-Key: super-secret-key" \
  http://localhost:8087/api/recommend/user123?n=10

# Get popular items
curl -H "X-API-Key: super-secret-key" \
  http://localhost:8087/api/popular?n=10

# Get latest items
curl -H "X-API-Key: super-secret-key" \
  http://localhost:8087/api/latest?n=10
```

## Troubleshooting

### No recommendations returned
- Wait for Gorse to process (24h refresh period by default)
- Check dashboard at http://localhost:8088 for job status
- Ensure you have enough interactions (need multiple users and items)

### API errors
- Verify Gorse containers are running: `docker ps`
- Check API key matches in config.toml
- View logs: `docker logs gorse_server`

### Firestore connection issues
- Verify firebase-credentials.json path is correct
- Check Firebase project ID matches
- Ensure service account has Firestore permissions

## Next Steps

1. **Schedule regular syncs** using cron or a scheduler
2. **Incremental updates** - Modify script to only sync new/changed data
3. **Monitor Gorse dashboard** at http://localhost:8088
4. **Integrate recommendations** into your application
