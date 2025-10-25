# ============================================================
# RESET GORSE DATABASE AND RE-SYNC WITH MASTER CATEGORIES
# ============================================================
# This script clears all old data and syncs fresh with the
# new master category system (17 standardized categories)

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "GORSE DATABASE RESET & MASTER CATEGORY SYNC" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Step 1: Stop containers
Write-Host "[1/5] Stopping Docker containers..." -ForegroundColor Yellow
docker-compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to stop containers" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Containers stopped`n" -ForegroundColor Green

# Step 2: Remove MongoDB volume (optional, commented out by default)
Write-Host "[2/5] Checking for persistent data volumes..." -ForegroundColor Yellow
$volumes = docker volume ls --format "{{.Name}}" | Where-Object { $_ -like "*mongo*" }
if ($volumes) {
    Write-Host "  Found volumes: $($volumes -join ', ')" -ForegroundColor White
    Write-Host "  To delete volumes, run: docker volume rm $($volumes -join ' ')" -ForegroundColor Gray
    Write-Host "  (Skipping for now - data will be overwritten)`n" -ForegroundColor Gray
} else {
    Write-Host "  [OK] No persistent volumes found`n" -ForegroundColor Green
}

# Step 3: Start containers fresh
Write-Host "[3/5] Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Containers started`n" -ForegroundColor Green

# Step 4: Wait for services to be ready
Write-Host "[4/5] Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
for ($i = 30; $i -gt 0; $i--) {
    Write-Host "  $i seconds remaining..." -ForegroundColor Gray
    Start-Sleep -Seconds 1
}
Write-Host "  [OK] Services should be ready`n" -ForegroundColor Green

# Step 5: Check if we're in conda environment
Write-Host "[5/5] Running master category sync..." -ForegroundColor Yellow
$condaEnv = $env:CONDA_DEFAULT_ENV
if ($condaEnv -eq "gorse_sync") {
    Write-Host "  [OK] Conda environment 'gorse_sync' is active" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Not in 'gorse_sync' conda environment" -ForegroundColor Yellow
    Write-Host "  Current environment: $condaEnv" -ForegroundColor Gray
    Write-Host "  Please run: conda activate gorse_sync" -ForegroundColor Yellow
    Write-Host "`nContinuing anyway...`n" -ForegroundColor Gray
}

# Run the sync
python sync_with_categories.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n  ERROR: Sync failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "[OK] RESET AND SYNC COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Check stats: Invoke-RestMethod http://localhost:8088/api/dashboard/stats" -ForegroundColor White
Write-Host "  2. Should show ~162 users (only human users with interests)" -ForegroundColor White
Write-Host "  3. Should show 17 unique master categories" -ForegroundColor White
Write-Host "  4. Wait 5-10 minutes for model training" -ForegroundColor White
Write-Host "  5. Test recommendations!" -ForegroundColor White
Write-Host "`nDashboard: http://localhost:8088" -ForegroundColor Cyan
