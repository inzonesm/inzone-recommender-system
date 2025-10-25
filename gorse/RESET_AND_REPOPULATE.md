# 🔄 Complete Gorse Reset and Repopulation Guide

This guide shows you how to completely clear the Gorse recommendation engine cache and data, then repopulate it from Firestore.

## 📋 Table of Contents
1. [Quick Reset (Keep MongoDB Data)](#quick-reset)
2. [Full Reset (Clear Everything)](#full-reset)
3. [Repopulate from Firestore](#repopulate)
4. [Verification](#verification)

---

## 🔄 Option 1: Quick Reset (Keep MongoDB Data)

This restarts Gorse containers and clears in-memory cache while keeping MongoDB data.

### Steps:

```powershell
# Navigate to Gorse directory
cd C:\Users\DW\InZone\recommender-system\gorse

# Stop all Gorse containers
docker-compose down

# Start containers again (cache will be cleared)
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
Start-Sleep -Seconds 30

# Check status
docker-compose ps
```

**When to use:** You want to clear cache but keep existing users/items/feedback data.

---

## 🗑️ Option 2: Full Reset (Clear Everything)

This completely removes ALL data including users, items, and feedback.

### Steps:

```powershell
# Navigate to Gorse directory
cd C:\Users\DW\InZone\recommender-system\gorse

# Stop all containers
docker-compose down

# Remove MongoDB data volume (⚠️ THIS DELETES EVERYTHING!)
Remove-Item -Recurse -Force .\mongo-data -ErrorAction SilentlyContinue

# Start fresh containers
docker-compose up -d

# Wait for services to be ready
Start-Sleep -Seconds 30

# Check status
docker-compose ps
```

**When to use:** You want a completely fresh start with no old data.

---

## 📥 Option 3: Repopulate from Firestore

After clearing cache/data, repopulate Gorse with fresh data from Firestore.

### Method A: Using Local Gorse (Recommended for Testing)

```powershell
# Navigate to Gorse directory
cd C:\Users\DW\InZone\recommender-system\gorse

# Make sure Gorse is running
docker-compose ps

# Run the sync script
python sync_firestore_to_gorse.py
```

**Expected Output:**
```
============================================================
Starting Firestore to Gorse Sync
============================================================

[1/3] Syncing Users...
  Fetching humanUsers...
  Fetching aiUsers...
Fetched 150 users from Firestore (humanUsers + aiUsers)
✓ Batch inserted 100 users
  Progress: 100/150 users
✓ Batch inserted 50 users
  Progress: 150/150 users

[2/3] Syncing Items...
  Fetching humanPosts...
  Fetching aiPosts...
Fetched 1000 items from Firestore (humanPosts + aiPosts)
✓ Batch inserted 100 items
  Progress: 100/1000 items
...
  Progress: 1000/1000 items

[3/3] Syncing Interactions...
  Fetching postLikes...
  Fetching postComments...
Fetched 5000 interactions from Firestore
✓ Batch inserted 100 interactions
...

============================================================
Sync completed!
============================================================
Total Users: 150
Total Items: 1000
Total Interactions: 5000
```

### Method B: Using Remote Gorse (Production)

```powershell
# Use the remote sync script
python sync_firestore_to_remote_gorse.py
```

This connects to your production Gorse at `34.145.126.145`.

---

## ✅ Verification

After repopulating, verify everything is working:

### 1. Check Gorse Dashboard

Open in browser: http://34.145.126.145:8088 (or http://localhost:8088 for local)

Look for:
- **Users count** should match your Firestore humanUsers + aiUsers count
- **Items count** should match your posts count
- **Feedback count** should show likes + comments

### 2. Test Recommendations API

```powershell
# Get recommendations for a user
curl -H "X-API-Key: super-secret-key" http://34.145.126.145:8087/api/recommend/USER_ID_HERE?n=10
```

Should return JSON with recommended post IDs.

### 3. Test Flask Backend

Restart your Flask backend and check logs when fetching feed:

```powershell
cd C:\Users\DW\InZone\inzone-flutter-app\z-inzoneapi
python app.py
```

Look for:
```
🎯 Gorse-powered recommendations: requesting 20 items
✅ Gorse returned 20 recommendations
📝 Returning 10 recommendations (will be marked as read when actually viewed)
🎯 Returning GORSE-POWERED recommendations
```

### 4. Test in Flutter App

1. Open your app on emulator
2. Navigate to feed
3. Scroll through posts
4. Check backend logs for: `👁️ User xxx... viewed post yyy...`

---

## 🐛 Troubleshooting

### Issue: "Connection refused" when running sync script

**Solution:** Make sure Gorse containers are running:
```powershell
docker-compose ps
# All containers should show "Up"
```

### Issue: Sync script takes too long

**Solution:** The script processes in batches of 100. For large datasets (10k+ items), this is normal.

### Issue: "Failed to insert" errors

**Solution:** Check Gorse logs:
```powershell
docker logs gorse_server
docker logs gorse_master
```

### Issue: Recommendations still showing old cached results

**Solution:** Cache expires after 1 hour (`cache_expire = "1h"` in config.toml). Either:
- Wait 1 hour for natural expiration
- Do a full reset (Option 2)
- Temporarily reduce cache time in config.toml to `"5m"` and restart

---

## 🔧 Advanced: Clear Only Cache (Not Data)

If you want to force Gorse to regenerate recommendations without losing data:

```powershell
# Connect to MongoDB and clear cache collection
docker exec -it gorse_mongo mongosh

# In MongoDB shell:
use gorse_cache
db.dropDatabase()
exit

# Restart Gorse services to regenerate cache
docker-compose restart gorse-master gorse-server gorse-worker
```

---

## 📝 Summary of Options

| Option | Use Case | MongoDB Data | Cache | Time |
|--------|----------|--------------|-------|------|
| **Quick Reset** | Clear cache only | ✅ Kept | ❌ Cleared | 30 sec |
| **Full Reset** | Fresh start | ❌ Deleted | ❌ Cleared | 30 sec |
| **Repopulate** | Load from Firestore | ✅ Populated | ✅ Generated | 2-5 min |
| **Cache Only** | Force re-recommendation | ✅ Kept | ❌ Cleared | 10 sec |

---

## ⚡ Quick Commands Reference

```powershell
# Stop Gorse
docker-compose down

# Start Gorse
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Sync from Firestore
python sync_firestore_to_gorse.py

# Full reset
docker-compose down; Remove-Item -Recurse -Force .\mongo-data; docker-compose up -d
```

---

**Pro Tip:** After a full reset and repopulation, give Gorse 5-10 minutes to:
- Train initial models (`model_fit_period = "15m"`)
- Generate recommendations (`refresh_recommend_period = "6h"`)
- Build cache (`cache_expire = "1h"`)

Check the dashboard to see training progress!
