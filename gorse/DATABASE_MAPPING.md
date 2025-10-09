# Database Structure Analysis & Script Customization

## Your Firestore Structure

### Collections Found:
- **users** - User profiles (human and AI)
- **humanPosts** - Posts created by human users
- **aiPosts** - Posts created by AI users
- **postLikes** - Like interactions
- **postComments** - Comment interactions
- **reposts** - Repost actions
- And 23 other collections...

## What Was Customized in sync_firestore_to_gorse.py

### 1. Users Mapping (`fetch_users_from_firestore`)

**Source:** `users` collection

**Field Mappings:**
```
Firestore Field → Gorse Property
─────────────────────────────────
uid             → UserId
user_name       → Comment (display name)
categories      → Labels (user interests)
age             → Labels (as "age_XX")
gender          → Labels (as "gender_XX")
parent          → Labels (flag as "parent")
ai              → Labels (flag as "ai_user")
```

**Example User:**
```json
{
  "UserId": "3Iu5LiGyraXFYXMDYXAO4pBV9Tm1",
  "Labels": ["sports", "tech", "age_25", "gender_male", "parent"],
  "Comment": "John Doe"
}
```

### 2. Items Mapping (`fetch_items_from_firestore`)

**Sources:** `humanPosts` + `aiPosts` collections

**Field Mappings:**
```
Firestore Field → Gorse Property
─────────────────────────────────
id/doc.id       → ItemId
category        → Categories (list of categories)
date_posted     → Timestamp
user_name       → Comment (post author)
has_image       → Labels ("has_image")
has_video       → Labels ("has_video")
[collection]    → Labels ("human_post" or "ai_post")
```

**Example Post:**
```json
{
  "ItemId": "2biQrHHYMSuFF5EEkU7a",
  "Categories": ["beverage", "environment", "humor"],
  "Labels": ["human_post", "has_image"],
  "Timestamp": "2025-05-30T21:43:26.311000+00:00",
  "Comment": "Michael Kame"
}
```

### 3. Interactions Mapping (`fetch_interactions_from_firestore`)

**Sources:**
- `postLikes` collection → "like" feedback
- `postComments` collection → "comment" feedback

**Field Mappings:**

**For Likes:**
```
Firestore Field → Gorse Property
─────────────────────────────────
user_id         → UserId
post_id         → ItemId
timestamp       → Timestamp
[fixed]         → FeedbackType = "like"
```

**For Comments:**
```
Firestore Field → Gorse Property
─────────────────────────────────
comments[].userId → UserId
postId            → ItemId
comments[].timestamp → Timestamp
[fixed]           → FeedbackType = "comment"
```

**Example Interaction:**
```json
{
  "FeedbackType": "like",
  "UserId": "29zVzxnwZCq7yCHrHiyY",
  "ItemId": "AT9MlXBOvQcCO8KwmzgQ",
  "Timestamp": "2025-08-20T19:04:27.433170+00:00"
}
```

## Gorse Configuration Match

Your `config.toml` defines:
```toml
positive_feedback_types = ["like","share","comment"]
read_feedback_types     = ["read"]
```

**Current Implementation:**
- ✅ "like" - Mapped from `postLikes`
- ✅ "comment" - Mapped from `postComments`
- ❌ "share" - Not yet mapped (would need `reposts` collection)
- ❌ "read" - Not yet mapped (would need view tracking)

## Optional Enhancements

### Add Share Feedback

Add this to `fetch_interactions_from_firestore()`:

```python
# Fetch shares/reposts
print("  Fetching reposts...")
reposts_ref = db.collection('reposts')
for doc in reposts_ref.stream():
    repost_data = doc.to_dict()
    interaction = {
        "FeedbackType": "share",
        "UserId": repost_data.get('user_id', ''),
        "ItemId": repost_data.get('post_id', ''),
        "Timestamp": # extract timestamp
    }
    if interaction["UserId"] and interaction["ItemId"]:
        interactions.append(interaction)
```

### Add Read/View Feedback

If you track individual views (not just viewcount), create view events:

```python
# Fetch views (if you have a views collection)
views_ref = db.collection('postViews')  # if exists
for doc in views_ref.stream():
    view_data = doc.to_dict()
    interaction = {
        "FeedbackType": "read",
        "UserId": view_data.get('user_id', ''),
        "ItemId": view_data.get('post_id', ''),
        "Timestamp": # extract timestamp
    }
    interactions.append(interaction)
```

## Ready to Run

The script is now customized for your database structure. Run:

```bash
conda activate gorse
python sync_firestore_to_gorse.py
```

## What to Expect

1. **Users:** All users from `users` collection with their interests and demographics
2. **Items:** All posts from both `humanPosts` and `aiPosts` with categories
3. **Interactions:** All likes and comments

After sync, Gorse will:
- Build user preference profiles based on categories they engage with
- Recommend posts similar to what users liked/commented on
- Use collaborative filtering to suggest posts liked by similar users
