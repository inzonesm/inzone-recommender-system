"""
Sync users and items from Firestore to REMOTE Gorse Recommender System (GCP)
This version can be run from your local machine to sync to the remote server.
"""
import requests
import json
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - REMOTE SERVER (Updated for new instance)
GORSE_API_URL = os.getenv("GORSE_API_URL", "http://34.145.126.145:8087")
GORSE_API_KEY = os.getenv("GORSE_API_KEY", "super-secret-key")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")

print(f"[*] Connecting to remote Gorse server: {GORSE_API_URL}")

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
        """Test if we can connect to the remote Gorse server"""
        try:
            url = f"{self.api_url}/api/users"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code in [200, 401]:
                print(f"[OK] Connection successful to {self.api_url}")
                return True
            else:
                print(f"[ERROR] Connection failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            return False
    
    def insert_user(self, user_id: str, labels: List[str] = None, comment: str = ""):
        """Insert a user into Gorse"""
        url = f"{self.api_url}/api/user"
        data = {
            "UserId": user_id,
            "Labels": labels or [],
            "Comment": comment
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"[OK] User inserted: {user_id}")
        else:
            print(f"[ERROR] Failed to insert user {user_id}: {response.text}")
        return response
    
    def insert_users_batch(self, users: List[Dict[str, Any]]):
        """Insert multiple users in batch"""
        url = f"{self.api_url}/api/users"
        response = requests.post(url, headers=self.headers, json=users)
        if response.status_code == 200:
            print(f"[OK] Batch inserted {len(users)} users")
        else:
            print(f"[ERROR] Failed to batch insert users: {response.text}")
        return response
    
    def insert_item(self, item_id: str, is_hidden: bool = False, 
                    categories: List[str] = None, timestamp: str = None,
                    labels: List[str] = None, comment: str = ""):
        """Insert an item into Gorse"""
        url = f"{self.api_url}/api/item"
        data = {
            "ItemId": item_id,
            "IsHidden": is_hidden,
            "Categories": categories or [],
            "Timestamp": timestamp or datetime.now().isoformat(),
            "Labels": labels or [],
            "Comment": comment
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"[OK] Item inserted: {item_id}")
        else:
            print(f"[ERROR] Failed to insert item {item_id}: {response.text}")
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
    
    def insert_feedback(self, feedback_type: str, user_id: str, item_id: str, 
                       timestamp: str = None):
        """Insert feedback (like, read, share, comment, etc.)"""
        url = f"{self.api_url}/api/feedback"
        data = [{
            "FeedbackType": feedback_type,
            "UserId": user_id,
            "ItemId": item_id,
            "Timestamp": timestamp or datetime.now().isoformat()
        }]
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"[OK] Feedback inserted: {user_id} -> {item_id} ({feedback_type})")
        else:
            print(f"[ERROR] Failed to insert feedback: {response.text}")
        return response
    
    def get_stats(self):
        """Get current system stats from remote server"""
        try:
            dashboard_url = self.api_url.replace(":8087", ":8088")
            url = f"{dashboard_url}/api/dashboard/stats"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Warning: Could not fetch stats: {e}")
            return None


def fetch_users_from_firestore():
    """
    Fetch users from Firestore 'humanUsers' and 'aiUsers' collections
    Maps uid/doc.id, name, interests, personality, etc.
    """
    users = []
    
    # Fetch human users
    print("  Fetching humanUsers...")
    human_users_ref = db.collection('humanUsers')
    for doc in human_users_ref.stream():
        user_data = doc.to_dict()
        
        # Build labels from user attributes
        labels = []
        
        # Add interests (categories)
        if 'interests' in user_data and user_data['interests']:
            if isinstance(user_data['interests'], list):
                labels.extend(user_data['interests'])
            else:
                labels.append(str(user_data['interests']))
        
        user = {
            "UserId": user_data.get('uid', doc.id),  # Use uid field or doc ID
            "Labels": labels,
            "Comment": user_data.get('name', '') or user_data.get('email', '')
        }
        users.append(user)
    
    # Fetch AI users
    print("  Fetching aiUsers...")
    ai_users_ref = db.collection('aiUsers')
    for doc in ai_users_ref.stream():
        user_data = doc.to_dict()
        
        # Build labels from AI user attributes
        labels = ['ai_user']
        
        # Add personality
        if 'personality' in user_data and user_data['personality']:
            labels.append(f"personality_{user_data['personality']}")
        
        # Add sub_category
        if 'sub_category' in user_data and user_data['sub_category']:
            if isinstance(user_data['sub_category'], list):
                labels.extend(user_data['sub_category'])
            else:
                labels.append(str(user_data['sub_category']))
        
        user = {
            "UserId": doc.id,  # AI users use doc ID
            "Labels": labels,
            "Comment": user_data.get('name', '')
        }
        users.append(user)
    
    print(f"Fetched {len(users)} users from Firestore (humanUsers + aiUsers)")
    return users


def fetch_items_from_firestore():
    """
    Fetch items (posts) from both humanPosts and aiPosts collections
    Combines both collections with appropriate labels
    """
    items = []
    
    # Fetch human posts
    print("  Fetching humanPosts...")
    human_posts_ref = db.collection('humanPosts')
    for doc in human_posts_ref.stream():
        item_data = doc.to_dict()
        
        # Extract categories (main content categories)
        categories = item_data.get('category', [])
        if not isinstance(categories, list):
            categories = [categories] if categories else ['general']
        
        # Build labels (metadata tags)
        labels = ['human_post']
        if item_data.get('has_image'):
            labels.append('has_image')
        if item_data.get('has_video'):
            labels.append('has_video')
        
        # Convert timestamp
        timestamp = item_data.get('date_posted')
        if timestamp:
            timestamp = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
        else:
            timestamp = datetime.now().isoformat()
        
        item = {
            "ItemId": item_data.get('id') or doc.id,
            "IsHidden": False,
            "Categories": labels,  # Metadata becomes Categories for filtering
            "Timestamp": timestamp,
            "Labels": categories,  # Content categories become Labels
            "Comment": item_data.get('user_name', '')
        }
        items.append(item)
    
    # Fetch AI posts
    print("  Fetching aiPosts...")
    ai_posts_ref = db.collection('aiPosts')
    for doc in ai_posts_ref.stream():
        item_data = doc.to_dict()
        
        # Extract categories (main content categories)
        categories = item_data.get('category', [])
        if not isinstance(categories, list):
            categories = [categories] if categories else ['general']
        
        # Build labels (metadata tags)
        labels = ['ai_post']
        if item_data.get('has_image'):
            labels.append('has_image')
        if item_data.get('has_video'):
            labels.append('has_video')
        
        # Convert timestamp
        timestamp = item_data.get('date_posted')
        if timestamp:
            timestamp = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
        else:
            timestamp = datetime.now().isoformat()
        
        item = {
            "ItemId": item_data.get('id') or doc.id,
            "IsHidden": False,
            "Categories": labels,  # Metadata becomes Categories for filtering
            "Timestamp": timestamp,
            "Labels": categories,  # Content categories become Labels
            "Comment": item_data.get('user_name', '')
        }
        items.append(item)
    
    print(f"Fetched {len(items)} items from Firestore (humanPosts + aiPosts)")
    return items


def fetch_interactions_from_firestore():
    """
    Fetch user interactions from postLikes and postComments collections
    Maps to Gorse feedback types: like, comment, read (from viewcount)
    """
    interactions = []
    
    # Fetch likes
    print("  Fetching postLikes...")
    likes_ref = db.collection('postLikes')
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
    
    # Fetch comments
    print("  Fetching postComments...")
    comments_ref = db.collection('postComments')
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
                            # Parse string timestamp if needed
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
    
    print(f"Fetched {len(interactions)} interactions from Firestore")
    return interactions


def main():
    """Main function to sync Firestore data to REMOTE Gorse"""
    print("=" * 60)
    print("Starting Firestore to REMOTE Gorse Sync")
    print(f"Target Server: {GORSE_API_URL}")
    print("=" * 60)
    
    # Initialize Gorse client
    gorse = GorseClient(GORSE_API_URL, GORSE_API_KEY)
    
    # Test connection first
    print("\n[*] Testing connection to remote Gorse server...")
    if not gorse.test_connection():
        print("\n[X] Cannot connect to remote server. Please check:")
        print("  1. Server is running: docker-compose ps")
        print("  2. Firewall rules allow port 8087")
        print("  3. API key is correct")
        print(f"  4. URL is correct: {GORSE_API_URL}")
        return
    
    # Get current stats before sync
    print("\n[*] Current system stats before sync:")
    stats_before = gorse.get_stats()
    if stats_before:
        print(f"  Users: {stats_before.get('NumUsers', 0)}")
        print(f"  Items: {stats_before.get('NumItems', 0)}")
        print(f"  Feedback: {stats_before.get('NumTotalPosFeedback', 0)}")
    
    # Step 1: Sync Users
    print("\n[1/3] Syncing Users...")
    users = fetch_users_from_firestore()
    if users:
        # Insert users in smaller batches to avoid timeout
        batch_size = 100
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            gorse.insert_users_batch(batch)
            print(f"  Progress: {min(i + batch_size, len(users))}/{len(users)} users")
    
    # Step 2: Sync Items
    print("\n[2/3] Syncing Items...")
    items = fetch_items_from_firestore()
    if items:
        # Insert items in smaller batches to avoid timeout
        batch_size = 100
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            gorse.insert_items_batch(batch)
            print(f"  Progress: {min(i + batch_size, len(items))}/{len(items)} items")
    
    # Step 3: Sync Interactions/Feedback
    print("\n[3/3] Syncing Interactions...")
    interactions = fetch_interactions_from_firestore()
    if interactions:
        # Insert feedback in batches
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
                print(f"  Progress: {min(i + batch_size, len(interactions))}/{len(interactions)} interactions")
            else:
                print(f"[ERROR] Failed to insert interactions batch: {response.text}")
    
    # Get stats after sync
    print("\n[*] System stats after sync:")
    stats_after = gorse.get_stats()
    if stats_after:
        print(f"  Users: {stats_after.get('NumUsers', 0)}")
        print(f"  Items: {stats_after.get('NumItems', 0)}")
        print(f"  Feedback: {stats_after.get('NumTotalPosFeedback', 0)}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Sync completed successfully!")
    print("=" * 60)
    print(f"Total Users Synced: {len(users)}")
    print(f"Total Items Synced: {len(items)}")
    print(f"Total Interactions Synced: {len(interactions)}")
    print("\n[*] You can now access recommendations via:")
    dashboard_url = GORSE_API_URL.replace(":8087", ":8088")
    print(f"  - Dashboard: {dashboard_url}")
    print(f"  - API: {GORSE_API_URL}/api/recommend/{{user_id}}?n=10")
    print(f"\n[*] Test with: {GORSE_API_URL}/api/users")


if __name__ == "__main__":
    main()
