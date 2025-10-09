# Quick Reference: Your Customized Gorse Setup

## ✅ What's Been Done

1. **Analyzed your Firestore structure** (29 collections found)
2. **Customized the sync script** for your specific database
3. **Mapped your data** to Gorse's recommendation engine

## 🗂️ Your Data Mapping

| Firestore | Gorse Role | What It Does |
|-----------|------------|--------------|
| `users` collection | Users | People who get recommendations |
| `humanPosts` + `aiPosts` | Items | Content to recommend |
| `postLikes` | Feedback (like) | Positive signal for recommendations |
| `postComments` | Feedback (comment) | Positive signal for recommendations |

## 🚀 How to Run

```bash
# 1. Activate conda environment
conda activate gorse

# 2. Run the sync script
python sync_firestore_to_gorse.py

# 3. Check Gorse dashboard
# Open: http://localhost:8088
```

## 📊 What Gets Synced

### Users
- **Total**: All users in `users` collection
- **Properties**: username, age, gender, interests, AI/parent flags
- **Used for**: Building user preference profiles

### Posts/Items
- **Total**: All posts from `humanPosts` + `aiPosts`
- **Categories**: Extracted from `category` field (e.g., "Gaming", "Education", "outdoor_adventures")
- **Labels**: Post type (human/AI), media flags (has_image, has_video)

### Interactions
- **Likes**: From `postLikes` collection → "like" feedback
- **Comments**: From `postComments` collection → "comment" feedback
- **Total**: All historical interactions with timestamps

## 🎯 How Recommendations Work

1. **Content-Based**: Recommends posts with similar categories to what user liked
2. **Collaborative Filtering**: Recommends posts liked by similar users
3. **Category Matching**: Uses user's interest categories to match with post categories

## 🔧 Testing Recommendations

After syncing, test the API:

```bash
# Get recommendations for a specific user
curl -H "X-API-Key: super-secret-key" \
  "http://localhost:8087/api/recommend/3Iu5LiGyraXFYXMDYXAO4pBV9Tm1?n=10"

# Get popular posts
curl -H "X-API-Key: super-secret-key" \
  "http://localhost:8087/api/popular?n=20"

# Get latest posts
curl -H "X-API-Key: super-secret-key" \
  "http://localhost:8087/api/latest?n=20"
```

## 📝 Next Steps

1. **Run the sync** to populate Gorse with your data
2. **Check dashboard** at http://localhost:8088 to see statistics
3. **Wait for processing** - Gorse refreshes recommendations every 24h (configurable)
4. **Integrate API** into your application to serve recommendations

## 🔄 Keeping Data in Sync

- **Manual**: Run `python sync_firestore_to_gorse.py` whenever needed
- **Scheduled**: Set up a cron job to run daily
- **Real-time**: Modify your app to call Gorse API when users create posts/likes

## 📚 Documentation Files

- `sync_firestore_to_gorse.py` - Main sync script
- `DATABASE_MAPPING.md` - Detailed field mappings
- `SYNC_README.md` - General usage guide
- `CONDA_ENV.md` - Environment setup
- `config.toml` - Gorse configuration

## 🆘 Troubleshooting

**No recommendations?**
- Check dashboard for job status
- Ensure users have interaction history
- Wait for background worker to process (can take time)

**API returns empty?**
- Verify data was synced: Check dashboard statistics
- Check logs: `docker logs gorse_server`
- Ensure API key is correct

**Script errors?**
- Check Firebase credentials path
- Ensure Gorse containers are running: `docker ps`
- Verify collections exist in Firestore
