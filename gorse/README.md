# Gorse Recommender System - Server Deployment

A recommendation system powered by Gorse, MongoDB, and Firebase Firestore with **semantic label matching** using AI embeddings.

## ✨ Key Features

- 🤖 **Semantic Label Matching** - Uses AI to understand that "gaming" matches "video games", "fitness" matches "exercise", etc.
- 🎯 **Smart Cold Start** - New users get relevant recommendations immediately
- 🔄 **Real-time Sync** - Automatically syncs data from Firestore to Gorse
- 📊 **Multiple Strategies** - Combines collaborative filtering, content-based, and popularity-based recommendations
- 🚀 **Production Ready** - Dockerized deployment with MongoDB backend
- 💻 **No GPU Required** - Works perfectly on CPU-only servers (GPU optional for faster processing)

## 🚀 Quick Deployment

### Prerequisites
- Docker & Docker Compose installed
- Firebase credentials file (`firebase-credentials.json`)
- Python 3.8+ (for data sync)
- **No GPU required** - System works on CPU-only servers ✓

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/inzonesm/inzone-recommender-system.git
   cd inzone-recommender-system/gorse
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - `firebase-admin` - Firestore integration
   - `sentence-transformers` - Semantic matching (AI embeddings)
   - `torch` - Deep learning backend
   - `requests` - API communication

3. **Add Firebase credentials**
   ```bash
   nano firebase-credentials.json
   # Paste your Firebase credentials, save (Ctrl+X, Y, Enter)
   ```

4. **Start services**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Sync data from Firestore** (with semantic matching)
   ```bash
   python sync_firestore_to_gorse.py
   ```
   
   First run will download AI model (~80MB) and may take 1-2 minutes.

6. **Verify deployment**
   ```bash
   docker-compose ps
   curl http://localhost:8087/api/users
   curl http://localhost:8088/api/dashboard/stats
   ```

## 🧠 Semantic Matching

### What is Semantic Matching?

Instead of just exact string matching, our system uses AI to understand that:
- "gaming" is similar to "video games" and "esports"
- "fitness" is similar to "exercise" and "workout"  
- "nutrition&food" is similar to "healthy eating" and "recipes"

### How It Works

1. **AI Embeddings**: Converts labels into 384-dimensional vectors
2. **Cosine Similarity**: Computes similarity between user interests and post categories
3. **Smart Expansion**: Automatically expands user interests with related categories

### Testing Semantic Matching

```bash
# Test 1: Test the semantic matcher alone
python test_semantic_matching.py

# Test 2: Test full integration with Gorse
python test_gorse_integration.py
```

**Test 1** shows you how different labels match:
```
✅ 'nutrition&food' ↔ 'healthy eating'
   Similarity: 0.872 → MATCH

✅ 'gaming' ↔ 'video games'
   Similarity: 0.891 → MATCH
```

**Test 2** verifies the complete flow:
- Inserts test users with expanded labels
- Verifies labels are stored in Gorse correctly
- Checks label overlap between users and items
- Tests recommendation API

✅ 'gaming' ↔ 'video games'
   Similarity: 0.891 → MATCH
```

### Configuration

Edit `sync_firestore_to_gorse.py`:

```python
# Enable/disable semantic matching
ENABLE_SEMANTIC_MATCHING = True

# Adjust similarity threshold (0-1)
semantic_matcher = SemanticLabelMatcher(
    similarity_threshold=0.5  # Higher = more strict
)
```

**See [SEMANTIC_MATCHING_GUIDE.md](SEMANTIC_MATCHING_GUIDE.md) for detailed documentation.**

## 📋 Services

- **Gorse Master** (Port 8088) - Dashboard and statistics
- **Gorse Server** (Port 8087) - REST API for recommendations
- **Gorse Worker** - Background processing and model training
- **MongoDB** (Port 27017) - Data storage (internal only)

## 🔧 Management Commands

```bash
# View logs
docker-compose logs -f gorse-master
docker-compose logs -f gorse-server

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Reset and rebuild
docker-compose down -v  # ⚠️ Deletes all data
docker-compose up -d
python sync_firestore_to_gorse.py

# Update from git
git pull origin main
docker-compose down
docker-compose up -d
```

## 📊 API Endpoints

### Basic Endpoints

- **Get Users**: `GET /api/users`
- **Get Items**: `GET /api/items`
- **Get User**: `GET /api/user/{user_id}`
- **Get Item**: `GET /api/item/{item_id}`

### Recommendation Endpoints

- **Get Recommendations**: `GET /api/recommend/{user_id}?n=10`
- **Get Item Neighbors**: `GET /api/item/{item_id}/neighbors?n=10`
- **Get Popular Items**: `GET /api/popular?n=10`
- **Get Latest Items**: `GET /api/latest?n=10`

### Dashboard (Port 8088)

- **Stats**: `GET http://localhost:8088/api/dashboard/stats`
- **Web UI**: `http://localhost:8088`

**Authentication**: Use header `X-API-Key: super-secret-key`

Example:
```bash
curl -H "X-API-Key: super-secret-key" \
  "http://localhost:8087/api/recommend/user123?n=10"
```

## 🔄 Data Sync

### Manual Sync

```bash
# Sync all data from Firestore to Gorse (with semantic matching)
python sync_firestore_to_gorse.py

# Restart master to update stats
docker-compose restart gorse-master
```

### What Gets Synced

1. **Users** (from `humanUsers` and `aiUsers` collections)
   - User IDs, interests, personality traits
   - Labels are normalized and semantically expanded
   
2. **Items** (from `humanPosts` and `aiPosts` collections)
   - Post IDs, categories, timestamps
   - Labels are normalized for better matching
   
3. **Interactions** (from `postLikes` and `postComments` collections)
   - Likes, comments, reads
   - Used for collaborative filtering

### Automated Sync (Optional)

Set up a cron job to sync periodically:

```bash
# Edit crontab
crontab -e

# Add line to sync every hour
0 * * * * cd /path/to/gorse && /path/to/python sync_firestore_to_gorse.py >> sync.log 2>&1
```

## 📚 Configuration Files

- **config.toml** - Gorse configuration
  - Recommendation algorithms (collaborative, content-based, etc.)
  - Model training schedules
  - Exploration strategies
  - See [COLD_START_GUIDE.md](COLD_START_GUIDE.md) for optimization tips
  
- **sync_firestore_to_gorse.py** - Data sync script
  - Firestore to Gorse synchronization
  - Label normalization
  - Semantic matching integration
  
- **semantic_label_matcher.py** - AI-powered label matching
  - Word embeddings for semantic similarity
  - Cosine similarity computation
  - See [SEMANTIC_MATCHING_GUIDE.md](SEMANTIC_MATCHING_GUIDE.md)
  
- **docker-compose.yml** - Service definitions
- **requirements.txt** - Python dependencies

## 📖 Documentation

- **[README.md](README.md)** - This file, quick start guide
- **[GORSE_INTEGRATION_GUIDE.md](GORSE_INTEGRATION_GUIDE.md)** - Complete integration guide
- **[SEMANTIC_MATCHING_GUIDE.md](SEMANTIC_MATCHING_GUIDE.md)** - Detailed guide on AI-powered label matching
- **[GPU_REQUIREMENTS.md](GPU_REQUIREMENTS.md)** - GPU needs and CPU optimization
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference cheat sheet
- **[LABEL_NORMALIZATION.md](LABEL_NORMALIZATION.md)** - Label preprocessing and standardization
- **[COLD_START_GUIDE.md](COLD_START_GUIDE.md)** - Troubleshooting cold start issues
- **[GIT_DEPLOYMENT_GUIDE.md](GIT_DEPLOYMENT_GUIDE.md)** - Server deployment instructions
- **[RESET_AND_REPOPULATE.md](RESET_AND_REPOPULATE.md)** - Reset and rebuild guide

## 💻 System Requirements

### Minimum (Development)
```
CPU: 2-4 cores
RAM: 4-8GB
Storage: 20GB
GPU: Not required ✓
```

### Recommended (Production)
```
CPU: 4-8 cores
RAM: 8-16GB
Storage: 50GB SSD
GPU: Optional (2-3x faster sync)
```

**See [GPU_REQUIREMENTS.md](GPU_REQUIREMENTS.md) for detailed performance analysis.**

## 🔒 Security Notes

- MongoDB is bound to localhost only (not exposed externally)
- Change the default API key in `docker-compose.yml` and `config.toml`:
  ```yaml
  environment:
    GORSE_SERVER_API_KEY: "your-secret-key-here"
  ```
- Never commit `firebase-credentials.json` to git (already in .gitignore)
- Use HTTPS in production with a reverse proxy (nginx/traefik)

---

**Repository**: https://github.com/inzonesm/inzone-recommender-system  
**Gorse Docs**: https://gorse.io/docs/master/
