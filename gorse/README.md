# Gorse Recommender System - Server Deployment

A recommendation system powered by Gorse, MongoDB, and Firebase Firestore.

## 🚀 Quick Deployment

### Prerequisites
- Docker & Docker Compose installed
- Firebase credentials file (`firebase-credentials.json`)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/inzonesm/inzone-recommender-system.git
   cd inzone-recommender-system/gorse
   ```

2. **Add Firebase credentials**
   ```bash
   nano firebase-credentials.json
   # Paste your Firebase credentials, save (Ctrl+X, Y, Enter)
   ```

3. **Start services**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   docker-compose ps
   curl http://localhost:8087/api/users
   curl http://localhost:8088/api/dashboard/stats
   ```

## 📋 Services

- **Gorse Master** (Port 8088) - Dashboard and statistics
- **Gorse Server** (Port 8087) - REST API for recommendations
- **Gorse Worker** - Background processing and model training
- **MongoDB** (Port 27017) - Data storage (internal only)

## 🔧 Management Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update from git
git pull origin main
docker-compose down
docker-compose up -d
```

## 📊 API Endpoints

- **Get Users**: `GET /api/users`
- **Get Items**: `GET /api/items`
- **Get Recommendations**: `GET /api/recommend/{user_id}?n=10`
- **Dashboard Stats**: `GET http://localhost:8088/api/dashboard/stats` (port 8088)

**Authentication**: Use header `X-API-Key: super-secret-key`

## 🔄 Data Sync

To sync data from Firestore, run the sync script:

```bash
# Install Python dependencies (one time)
sudo apt install -y python3 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run sync
python sync_firestore_to_gorse.py

# Restart master to update stats
docker-compose restart gorse-master
```

## 📚 Configuration

- **docker-compose.yml** - Service definitions and ports
- **config.toml** - Gorse configuration (recommendation algorithms, database, etc.)
- **requirements.txt** - Python dependencies for sync script

## 🔒 Security Notes

- MongoDB is bound to localhost only (not exposed externally)
- Change the default API key in `docker-compose.yml` (line: `GORSE_SERVER_API_KEY`)
- Never commit `firebase-credentials.json` to git (already in .gitignore)

## 📖 Full Documentation

For detailed deployment instructions, see: [GIT_DEPLOYMENT_GUIDE.md](./GIT_DEPLOYMENT_GUIDE.md)

---

**Repository**: https://github.com/inzonesm/inzone-recommender-system  
**Gorse Docs**: https://gorse.io/docs/master/
