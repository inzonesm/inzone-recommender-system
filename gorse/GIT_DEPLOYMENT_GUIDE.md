# Git-Based Deployment Guide for Gorse on GCP

## 🎯 Overview
This guide shows how to deploy and update your Gorse recommender system using Git - the professional way!

**Your Repository:** https://github.com/inzonesm/inzone-recommender-system  
**Instance Type:** e2-micro (1 GB RAM, 2 vCPUs)  
**External IP:** 34.145.126.145  
**Region:** us-west1-b  

---

## 🚀 Initial Deployment (One-Time Setup)

### Step 1: Access Your GCP Server

**Browser SSH (Recommended):**
1. Go to: https://console.cloud.google.com/compute/instances?project=inzone-recommender
2. Find `gorse-server` (IP: 34.145.126.145)
3. Click the **SSH** button in the browser

**Or use command line:**
```powershell
gcloud compute ssh gorse-server --zone=us-west1-b
```

### Step 2: Install Docker and Docker Compose

Copy and paste these commands in your SSH terminal:

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Clean up
rm get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# IMPORTANT: Log out and log back in for docker group to take effect
echo "Docker installed! Now exit and reconnect for changes to take effect."
```

**After running the above, type `exit` and click SSH button again to reconnect.**

### Step 3: Clone Your Repository

```bash
# Clone your repository
cd ~
git clone https://github.com/inzonesm/inzone-recommender-system.git

# Navigate to gorse directory
cd inzone-recommender-system/gorse

# Verify files are there
ls -la
```

You should see files like: `docker-compose.yml`, `config.toml`, `README.md`, etc.

### Step 4: Setup Firebase Credentials

Your `firebase-credentials.json` is in `.gitignore` (for security), so you need to upload it:

**Method 1: Copy-Paste in Terminal (Easiest)**

```bash
cd ~/inzone-recommender-system/gorse

# Create the file
nano firebase-credentials.json
```

Then:
1. Open your local `firebase-credentials.json` in Notepad
2. Copy all content (Ctrl+A, Ctrl+C)
3. Paste in the nano editor (Right-click in terminal)
4. Press `Ctrl+X`, then `Y`, then `Enter` to save

**Method 2: Use GCP Cloud Shell Upload**

1. In GCP Console, click the Cloud Shell icon (>_) at the top
2. Click the ⋮ menu → Upload
3. Select your local `firebase-credentials.json`
4. In Cloud Shell, run:
```bash
gcloud compute scp ~/firebase-credentials.json gorse-server:~/inzone-recommender-system/gorse/ --zone=us-west1-b
```

**Verify the file:**
```bash
cd ~/inzone-recommender-system/gorse
ls -lh firebase-credentials.json
# Should show the file with size > 0
```

### Step 5: Start Gorse Services

```bash
cd ~/inzone-recommender-system/gorse

# Pull Docker images (this takes 2-3 minutes)
docker-compose pull

# Start services in detached mode
docker-compose up -d

# Wait 30 seconds for services to initialize
sleep 30

# Check status (all should show "Up")
docker-compose ps

# View logs to verify everything started correctly
docker-compose logs --tail=50
```

**Expected output from `docker-compose ps`:**
```
NAME                 STATUS
gorse_master         Up
gorse_mongo          Up
gorse_server         Up
gorse_worker         Up
```

If any service shows "Exited" or "Restarting", check logs:
```bash
docker-compose logs <service-name>
# Example: docker-compose logs gorse-server
```

### Step 6: Verify Deployment

**Test from the server terminal:**
```bash
# Test API (should return empty user list or data)
curl http://localhost:8087/api/users

# Test Dashboard stats
curl http://localhost:8088/api/dashboard/stats

# Check all containers are running
docker-compose ps
```

**Test from your local machine (PowerShell):**
```powershell
# Test API with authentication
Invoke-WebRequest -Uri "http://34.145.126.145:8087/api/users" -Headers @{"X-API-Key"="super-secret-key"}

# Test Dashboard
Invoke-WebRequest -Uri "http://34.145.126.145:8088/api/dashboard/stats"
```

**Open in your browser:**
- **Dashboard**: http://34.145.126.145:8088
- **API Users**: http://34.145.126.145:8087/api/users

✅ If you see JSON responses, deployment is successful!

---

## 🔥 Configure Firewall Rules (If Not Already Done)

If you can't access from your browser, add firewall rules:

```powershell
# From your local PowerShell:

# Allow API port 8087
gcloud compute firewall-rules create allow-gorse-server `
  --allow=tcp:8087 `
  --source-ranges=0.0.0.0/0 `
  --description="Allow Gorse API access"

# Allow Dashboard port 8088
gcloud compute firewall-rules create allow-gorse-dashboard `
  --allow=tcp:8088 `
  --source-ranges=0.0.0.0/0 `
  --description="Allow Gorse Dashboard access"

# Verify rules
gcloud compute firewall-rules list --filter="name~gorse"
```

---

## 🔄 Future Updates (Super Easy!)

When you make changes on your local machine and push to GitHub:

### On Your Local Machine:
```bash
# Make your changes
# Commit and push
git add .
git commit -m "Your update message"
git push origin main
```

### On Your GCP Server:
```bash
# SSH into server
cd ~/inzone-recommender-system/gorse

# Pull latest changes
git pull origin main

# Restart services to apply changes
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f
```

**That's it!** Your changes are deployed! 🎉

---

## 📝 Setup Python Sync Script (On Server)

If you want to run sync from the server:

```bash
cd ~/inzone-recommender-system/gorse

# Install Python and pip
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Test the sync script (local mode)
python sync_firestore_to_gorse.py

# Deactivate virtual environment when done
deactivate
```

**Or sync from your local machine (Recommended):**

Update the IP in your local `sync_firestore_to_remote_gorse.py` then run:
```powershell
cd C:\Users\87964\inzone-recommender-system\gorse
python sync_firestore_to_remote_gorse.py
```

### Setup Automatic Sync (Optional)

```bash
# Create a wrapper script
cat > ~/sync-gorse.sh << 'EOF'
#!/bin/bash
cd ~/inzone-recommender-system/gorse
source venv/bin/activate
python sync_firestore_to_gorse.py >> ~/gorse-sync.log 2>&1
deactivate
EOF

chmod +x ~/sync-gorse.sh

# Setup cron job (runs every hour)
crontab -e

# Add this line:
0 * * * * ~/sync-gorse.sh
```

---

## 🛠️ Useful Commands

### Docker Management
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f gorse-server

# Restart a service
docker-compose restart gorse-server

# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Rebuild and start (if you change docker-compose.yml)
docker-compose up -d --build
```

### Git Management
```bash
# Check current status
git status

# Pull latest changes
git pull origin main

# View commit history
git log --oneline -10

# Discard local changes (be careful!)
git reset --hard origin/main
```

### System Monitoring
```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check Docker resource usage
docker stats

# Check running processes
htop  # (install with: sudo apt install htop)
```

---

## 🔒 Security Best Practices

1. **Firebase Credentials**: Never commit `firebase-credentials.json` to Git
2. **API Keys**: Change the default `super-secret-key` in `docker-compose.yml`
3. **MongoDB**: Already configured to bind to localhost only
4. **Firewall**: Only ports 8087 and 8088 are exposed

---

## 📊 Monitoring & Troubleshooting

### Check if services are healthy
```bash
curl http://localhost:8087/api/users
curl http://localhost:8088/api/dashboard/stats
curl http://localhost:8088/api/dashboard/cluster
```

### View detailed logs
```bash
cd ~/inzone-recommender-system/gorse
docker-compose logs --tail=100 -f
```

### Restart if something goes wrong
```bash
docker-compose restart
```

### Complete reset (nuclear option)
```bash
docker-compose down -v  # Removes volumes too!
git pull origin main
docker-compose up -d
```

---

## 🎯 Advantages of This Approach

✅ **Version Control** - Track all changes  
✅ **Easy Updates** - Just `git pull` and restart  
✅ **Collaboration** - Team members can contribute  
✅ **Rollback** - Easy to revert to previous versions  
✅ **Documentation** - Commit messages track changes  
✅ **Professional** - Industry-standard deployment method  

---

## 💰 Cost Reminder

**Current Instance:** e2-micro (1 GB RAM, 2 vCPUs)
- **Instance**: FREE (Free Tier eligible - 1 per month)
- **30GB Standard Disk**: FREE (Free Tier)
- **Network egress**: First 1GB FREE per month
- **Region**: us-west1-b (Free Tier eligible region)

**Total: $0/month** within free tier limits! 🎉

**Note:** If you exceed free tier limits (multiple instances, >30GB disk, >1GB network), charges will apply.

---

## 🆘 Need Help?

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify services: `docker-compose ps`
3. Check disk space: `df -h`
4. Check memory: `free -h`
5. Restart services: `docker-compose restart`

---

## 📚 Next Steps

Once deployed:
1. ✅ Access dashboard: http://34.145.126.145:8088
2. ✅ Test API: http://34.145.126.145:8087/api/users
3. ✅ Update sync script IP to 34.145.126.145
4. ✅ Run sync script to import Firestore data
5. ✅ Restart gorse-master to see stats: `docker-compose restart gorse-master`
6. ✅ Monitor performance and logs

**Happy Deploying!** 🚀
