# Docker Worker Connection Fix

## Problem Discovered
User reported: "The recommendations are just showing the latest posts"

### Root Cause
The `gorse-worker` service in `docker-compose.yml` was **missing master connection configuration**.

```yaml
# BEFORE (BROKEN)
gorse-worker:
  image: zhenghaoz/gorse-worker:0.4.0
  container_name: gorse_worker
  volumes: ["./config.toml:/etc/gorse/config.toml:ro"]
  depends_on: ["gorse-master"]
  # ❌ NO command section - worker couldn't connect to master!
```

Worker was trying to connect to `127.0.0.1:8086` (localhost) instead of `gorse-master:8086`.

**Worker logs showed:**
```
"error": "rpc error: code = Unavailable desc = connection error: 
desc = \"transport: Error while dialing dial tcp 127.0.0.1:8086: connect: connection refused\""
"error": "current node isn't in worker nodes"
```

This caused:
- ❌ Worker couldn't communicate with master
- ❌ No personalized recommendations generated
- ❌ Gorse fell back to `fallback_recommend=["latest"]`
- ❌ All users saw only the newest posts

---

## Solution Applied

Added master connection configuration to `gorse-worker`:

```yaml
# AFTER (FIXED)
gorse-worker:
  image: zhenghaoz/gorse-worker:0.4.0
  container_name: gorse_worker
  command:
    - --master-host
    - gorse-master
    - --master-port
    - "8086"
  volumes: ["./config.toml:/etc/gorse/config.toml:ro"]
  depends_on: ["gorse-master"]
```

This matches the `gorse-server` configuration which was already correct.

---

## Verification

### Before Fix
```
Recommended Posts Timestamps:
  1. SVPFTc3NpO...  2025-10-24 10:54  ← Latest
  2. HMT3sEoyEg...  2025-10-23 17:23  ← Latest
  3. 40BHsmnVkP...  2025-10-23 17:23  ← Latest
  4. w8ncdluiW2...  2025-10-23 17:23  ← Latest
  5. 8PddAiAHYf...  2025-10-23 17:23  ← Latest
  
Actual Latest 10 Posts:
  1. SVPFTc3NpO...  2025-10-24 10:54
  2. HMT3sEoyEg...  2025-10-23 17:23
  3. 40BHsmnVkP...  2025-10-23 17:23
  ...

❌ Recommendations EXACTLY match "latest posts" - fallback mode!
```

### After Fix
```
David's Recommendations (with timestamps):
  1. 2022-11-05 20:00 - [creativity_art, entertainment_memes, ...] exploration
  2. 2024-07-26 04:57 - [health_healthy_habits, gaming_virtual_worlds, ...] ✓ MATCH
  3. 2025-06-20 18:18 - [creativity_art, travel_adventure, food_diy, ...] ✓ MATCH
  4. 2025-03-31 17:04 - [pets_wildlife, food_diy, ...] ✓ MATCH
  5. 2024-05-24 23:46 - [creativity_art, entertainment_memes, ...] exploration
  6. 2025-10-24 10:54 - [entertainment_memes, inclusivity, ...] exploration
  ...

✓ Personalized recommendations spanning 2022-2025!
✓ 5/10 posts match user interests (label-based)
✓ 5/10 posts for exploration/discovery
```

### Worker Logs After Fix
```
{"level":"warn","msg":"user is unpredictable","user_id":"2trGtmamfSaUJjnpTwIi8bsuofj1"}
{"level":"warn","msg":"user is unpredictable","user_id":"32xHolTTgTeGbOuvdqOEtLa8xqr2"}
...

✓ Worker successfully connected to master
✓ Worker actively generating recommendations
⚠️ "unpredictable" warnings = users with limited interaction history (expected)
```

---

## Current Status

### What's Working ✅
- Worker connected to master successfully
- Personalized recommendations being generated
- Item-based matching functional (50% match rate for test user David)
- Exploration/discovery working (healthy 50% non-matching posts)
- Recommendations span entire time range (2022-2025), not just latest

### What's Still Suboptimal ⚠️
- Match rate is 50% (expected 80-90% after clean sync)
- Reason: Mixed old/new data (343 user labels + 467 item labels vs expected ~17 each)
- Many users marked "unpredictable" due to limited interactions

### Next Steps
1. **Run database reset**: `.\reset_and_sync_clean.ps1`
   - This will clear old mixed data
   - Sync ONLY with master categories
   - Expected result: ~162 users, 1571 posts, ~17 labels each

2. **Wait for model retraining** (5-10 minutes after reset)
   - Model fit period: 15 minutes
   - Worker will regenerate recommendations with clean data

3. **Re-test recommendations**
   - Expected match rate: 80-90% (up from current 50%)
   - Remaining 10-20%: Healthy exploration/collaborative filtering

---

## Key Learnings

1. **Always specify master connection for workers**
   - Without `--master-host` and `--master-port`, workers default to localhost
   - In Docker, this causes "connection refused" errors

2. **Fallback behavior is sneaky**
   - When worker fails, Gorse silently falls back to "latest" posts
   - Looks like working system, but no personalization happening

3. **Check worker logs early**
   - Worker errors are diagnostic gold
   - Connection errors mean no personalization possible

4. **Docker networking requires explicit configuration**
   - Service names (e.g., `gorse-master`) are DNS names in Docker networks
   - Don't rely on defaults for multi-container communication

---

## Impact

**Before fix**: 0% personalization (all users saw identical "latest posts")  
**After fix**: 50% personalization (with mixed data), expected 80-90% after clean sync

This was a **critical bug** preventing the entire recommendation system from functioning correctly!
