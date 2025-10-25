"""
Sync users and items from Firestore to Gorse Recommender System
Using MASTER CATEGORY MAPPING for consistent tagging
"""
import requests
import json
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
from typing import List, Dict, Any
import re
from category_mapper import CategoryMapper

# Configuration
GORSE_API_URL = "http://localhost:8087"
GORSE_API_KEY = "super-secret-key"
FIREBASE_CREDENTIALS_PATH = "./firebase-credentials.json"

# Initialize Category Mapper
print("="*70)
print("FIRESTORE → GORSE SYNC (Master Category Mapping)")
print("="*70)
category_mapper = CategoryMapper(top_k=4)  # Map to top 4 master categories

# Initialize Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
initialize_app(cred)
db = firestore.client()


class GorseClient:
    """Client for interacting with Gorse API"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        """Test connection to Gorse server"""
        try:
            # Try to get users list - if it works, connection is good
            url = f"{self.api_url}/api/users?n=1"
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code in [200, 404]  # 404 is OK if no users yet
        except Exception as e:
            print(f"  Connection error: {e}")
            return False
    
    def get_stats(self):
        """Get system statistics"""
        try:
            url = f"{self.api_url.replace('8087', '8088')}/api/dashboard/stats"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def insert_users_batch(self, users: List[Dict[str, Any]]):
        """Insert multiple users in batch"""
        url = f"{self.api_url}/api/users"
        response = requests.post(url, headers=self.headers, json=users)
        if response.status_code == 200:
            print(f"[OK] Batch inserted {len(users)} users")
        else:
            print(f"[ERROR] Failed to batch insert users: {response.text}")
        return response
    
    def insert_items_batch(self, items: List[Dict[str, Any]]):
        """Insert multiple items in batch"""
        url = f"{self.api_url}/api/items"
        response = requests.post(url, headers=self.headers, json=items)
        if response.status_code == 200:
            print(f"[OK] Batch inserted {len(items)} items")
        else:
            print(f"[ERROR] Failed to batch insert items: {response.text}")
        return response


def fetch_users_from_firestore():
    """
    Fetch users from Firestore and map their interests to master categories
    """
    users = []
    
    # Fetch human users only (excluding AI users)
    print("\n[1/3] Fetching human users from Firestore...")
    human_users_ref = db.collection('humanUsers')
    count = 0
    
    for doc in human_users_ref.stream():
        user_data = doc.to_dict()
        count += 1
        
        # Get user interests
        interests = []
        if 'interests' in user_data and user_data['interests']:
            if isinstance(user_data['interests'], list):
                interests = [str(interest).lower().strip() for interest in user_data['interests']]
            else:
                interests = [str(user_data['interests']).lower().strip()]
        
        # Skip users with no interests
        if not interests:
            continue
        
        # Map interests to master categories
        master_categories = category_mapper.map_labels_to_categories(interests)
        
        # Show first 3 mappings as examples
        if count <= 3:
            print(f"\n  User {count}: {user_data.get('name', 'Unknown')}")
            print(f"    Original interests: {interests[:3]}")
            print(f"    → Master categories: {master_categories}")
        
        user = {
            "UserId": user_data.get('uid', doc.id),
            "Labels": master_categories,  # Use master categories as labels
            "Comment": user_data.get('name', '') or user_data.get('email', '')
        }
        users.append(user)
    
    print(f"\n  Total human users with interests: {len(users)}")
    return users


def fetch_items_from_firestore():
    """
    Fetch posts from Firestore and map their categories to master categories
    """
    items = []
    
    print("\n[2/3] Fetching posts from Firestore...")
    
    # Fetch human posts
    print("  Processing humanPosts...")
    human_posts_ref = db.collection('humanPosts')
    human_count = 0
    
    for doc in human_posts_ref.stream():
        item_data = doc.to_dict()
        human_count += 1
        
        # Extract post categories
        categories_raw = item_data.get('category', [])
        if not isinstance(categories_raw, list):
            categories_raw = [categories_raw] if categories_raw else []
        
        # Convert to lowercase strings
        categories = [str(cat).lower().strip() for cat in categories_raw if cat]
        
        # Skip posts with no categories
        if not categories:
            categories = ['general']
        
        # Map to master categories
        master_categories = category_mapper.map_labels_to_categories(categories)
        
        # Build metadata labels
        metadata_labels = ['human_post']
        if item_data.get('has_image'):
            metadata_labels.append('has_image')
        if item_data.get('has_video'):
            metadata_labels.append('has_video')
        
        # Convert timestamp
        timestamp = item_data.get('date_posted')
        if timestamp:
            timestamp = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
        else:
            timestamp = datetime.now().isoformat()
        
        item = {
            "ItemId": item_data.get('id') or doc.id,
            "IsHidden": False,
            "Categories": metadata_labels,  # human_post, has_image, etc.
            "Timestamp": timestamp,
            "Labels": master_categories,  # Master categories for matching
            "Comment": item_data.get('user_name', '')
        }
        items.append(item)
    
    # Fetch AI posts
    print("  Processing aiPosts...")
    ai_posts_ref = db.collection('aiPosts')
    ai_count = 0
    
    for doc in ai_posts_ref.stream():
        item_data = doc.to_dict()
        ai_count += 1
        
        # Extract post categories
        categories_raw = item_data.get('category', [])
        if not isinstance(categories_raw, list):
            categories_raw = [categories_raw] if categories_raw else []
        
        # Convert to lowercase strings
        categories = [str(cat).lower().strip() for cat in categories_raw if cat]
        
        # Skip posts with no categories
        if not categories:
            categories = ['general']
        
        # Map to master categories
        master_categories = category_mapper.map_labels_to_categories(categories)
        
        # Build metadata labels
        metadata_labels = ['ai_post']
        if item_data.get('has_image'):
            metadata_labels.append('has_image')
        if item_data.get('has_video'):
            metadata_labels.append('has_video')
        
        # Convert timestamp
        timestamp = item_data.get('date_posted')
        if timestamp:
            timestamp = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
        else:
            timestamp = datetime.now().isoformat()
        
        item = {
            "ItemId": item_data.get('id') or doc.id,
            "IsHidden": False,
            "Categories": metadata_labels,  # ai_post, has_image, etc.
            "Timestamp": timestamp,
            "Labels": master_categories,  # Master categories for matching
            "Comment": item_data.get('user_name', '')
        }
        items.append(item)
    
    # Show sample mappings
    if items:
        print(f"\n  Sample post mapping:")
        sample = items[0]
        print(f"    Post: {sample['Comment']}")
        print(f"    Master categories: {sample['Labels']}")
    
    print(f"\n  Total posts: {len(items)} (human: {human_count}, ai: {ai_count})")
    return items


def fetch_interactions_from_firestore():
    """
    Fetch user interactions from postLikes and postComments collections
    """
    interactions = []
    
    print("\n[3/3] Fetching interactions from Firestore...")
    
    # Fetch likes
    print("  Processing postLikes...")
    likes_ref = db.collection('postLikes')
    likes_count = 0
    
    for doc in likes_ref.stream():
        like_data = doc.to_dict()
        
        # Convert timestamp
        timestamp = like_data.get('timestamp')
        if timestamp:
            timestamp = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
        else:
            timestamp = datetime.now().isoformat()
        
        interaction = {
            "FeedbackType": "like",
            "UserId": like_data.get('user_id', ''),
            "ItemId": like_data.get('post_id', ''),
            "Timestamp": timestamp
        }
        
        if interaction["UserId"] and interaction["ItemId"]:
            interactions.append(interaction)
            likes_count += 1
    
    # Fetch comments
    print("  Processing postComments...")
    comments_ref = db.collection('postComments')
    comments_count = 0
    
    for doc in comments_ref.stream():
        comment_data = doc.to_dict()
        post_id = comment_data.get('postId', doc.id)
        
        # Each document contains an array of comments
        comments_list = comment_data.get('comments', [])
        if isinstance(comments_list, list):
            for comment in comments_list:
                if isinstance(comment, dict):
                    # Convert timestamp
                    timestamp_str = comment.get('timestamp', '')
                    try:
                        if timestamp_str:
                            timestamp = timestamp_str if isinstance(timestamp_str, str) else str(timestamp_str)
                        else:
                            timestamp = datetime.now().isoformat()
                    except:
                        timestamp = datetime.now().isoformat()
                    
                    interaction = {
                        "FeedbackType": "comment",
                        "UserId": comment.get('userId', ''),
                        "ItemId": post_id,
                        "Timestamp": timestamp
                    }
                    
                    if interaction["UserId"] and interaction["ItemId"]:
                        interactions.append(interaction)
                        comments_count += 1
    
    print(f"\n  Total interactions: {len(interactions)} (likes: {likes_count}, comments: {comments_count})")
    return interactions


def main():
    """Main function to sync Firestore data to Gorse"""
    
    # Initialize Gorse client
    gorse = GorseClient(GORSE_API_URL, GORSE_API_KEY)
    
    # Test connection
    print("\n[*] Testing connection to Gorse server...")
    if not gorse.test_connection():
        print("\n[ERROR] Cannot connect to Gorse server. Please check:")
        print("  1. Docker containers are running: docker-compose ps")
        print("  2. Run: docker-compose up -d")
        print("  3. Gorse server is at: " + GORSE_API_URL)
        return
    print("[OK] Connected to Gorse server")
    
    # Get current stats
    print("\n[*] Current system stats before sync:")
    stats_before = gorse.get_stats()
    if stats_before:
        print(f"  Users: {stats_before.get('NumUsers', 0)}")
        print(f"  Items: {stats_before.get('NumItems', 0)}")
        print(f"  Feedback: {stats_before.get('NumTotalPosFeedback', 0)}")
    
    # Fetch and sync users
    users = fetch_users_from_firestore()
    if users:
        print(f"\n[*] Syncing {len(users)} users to Gorse...")
        batch_size = 100
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            gorse.insert_users_batch(batch)
            print(f"  Progress: {min(i + batch_size, len(users))}/{len(users)} users")
    
    # Fetch and sync items
    items = fetch_items_from_firestore()
    if items:
        print(f"\n[*] Syncing {len(items)} posts to Gorse...")
        batch_size = 100
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            gorse.insert_items_batch(batch)
            print(f"  Progress: {min(i + batch_size, len(items))}/{len(items)} items")
    
    # Fetch and sync interactions
    interactions = fetch_interactions_from_firestore()
    if interactions:
        print(f"\n[*] Syncing {len(interactions)} interactions to Gorse...")
        batch_size = 100
        for i in range(0, len(interactions), batch_size):
            batch = interactions[i:i + batch_size]
            url = f"{GORSE_API_URL}/api/feedback"
            headers = {
                "X-API-Key": GORSE_API_KEY,
                "Content-Type": "application/json"
            }
            response = requests.post(url, headers=headers, json=batch)
            if response.status_code == 200:
                print(f"[OK] Batch inserted {len(batch)} interactions")
            else:
                print(f"[ERROR] Failed to insert interactions: {response.text}")
    
    # Final stats
    print("\n" + "="*70)
    print("[OK] SYNC COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"Total Users Synced: {len(users)}")
    print(f"Total Posts Synced: {len(items)}")
    print(f"Total Interactions Synced: {len(interactions)}")
    print(f"\n[*] Master Categories System:")
    print(f"    17 standardized categories")
    print(f"    Each user/post mapped to top 4 categories")
    print(f"    Consistent vocabulary across all content")
    
    print("\n[*] You can now access recommendations via:")
    print(f"  - Dashboard: http://localhost:8088")
    print(f"  - API: {GORSE_API_URL}/api/recommend/{{user_id}}?n=10")
    print("\n[*] Tip: Wait 5-10 minutes for Gorse to train the model")
    print("         Check logs with: docker-compose logs -f gorse-master")


if __name__ == "__main__":
    main()
