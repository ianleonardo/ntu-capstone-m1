# ⚡ QUICK FIX for Slow GCP Deployment

## 🔴 LATEST FIX: DataFrame Hashing Error (Feb 13, 2026)

### Issue: "TypeError: unhashable type: 'dict'" in Streamlit Cache

**Error message:**
```
Pandas DataFrame hash failed. Falling back to pickling the object.
TypeError: unhashable type: 'dict'
```

**Root cause:** Functions with `@st.cache_data` that accept DataFrames as parameters cause Streamlit to try hashing the DataFrame, which fails when columns contain dicts.

**Solution applied:**
✅ **Removed caching from transformation functions** - Only data loading is cached now
✅ **Follows Streamlit best practices** - Cache data loading, not transformations
✅ **No more hashing warnings** - App runs cleanly

**YOU MUST REDEPLOY** to apply this fix (see deployment command below).

---

## 🔴 CRITICAL FIX: Skills Loading Timeout

### Issue: App Stuck on "Running DataProcessor.load_skills_data()"

The 16MB skills file times out on Cloud Run. **Solution applied:**

✅ **Skills chart now has a toggle** - Users can disable it to skip loading
✅ **Better error handling** - App won't crash if skills fail to load  
✅ **Progress indicator** - Shows "Loading skills data (16MB)... This may take 5-10 seconds"

**Default behavior:** Skills loading is **enabled** but users can uncheck the box to skip it.

### Alternative: Disable Skills by Default on GCP

Edit `app_optimized.py` line 476:
```python
# Change from:
load_skills = st.checkbox("Load Skills Analysis", value=True, ...)

# To:
load_skills = st.checkbox("Load Skills Analysis", value=False, ...)
```

This makes skills **opt-in** instead of default, preventing the timeout issue.

---

## 🔴 Immediate Actions (Do This Now!)

### 1. Redeploy with Correct Settings

Run this command to fix the slow loading issue:

```bash
gcloud run deploy workforce-portal \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 1
```

**This fixes:**
- ✅ Uses `app_optimized.py` (via updated Dockerfile)
- ✅ Allocates 2GB RAM (was probably 512MB-1GB)
- ✅ Uses 2 CPUs (was probably 1 CPU)
- ✅ Keeps 1 instance warm (no cold starts)

### 2. Why It Was Slow

**Problem 1: Using `app.py` instead of `app_optimized.py`**
- Original app does heavy processing on every load
- Optimized version has better caching

**Problem 2: Insufficient Resources**
- Default Cloud Run: 512MB RAM, 1 CPU
- Your data: 42MB parquet files + processing
- Result: Memory thrashing, slow processing

**Problem 3: Cold Starts**
- Default: `--min-instances 0`
- First request after idle: 10-20 second delay
- Solution: `--min-instances 1` keeps it warm

## 📊 Expected Performance After Fix

| Metric | Before | After |
|--------|--------|-------|
| Cold Start | 15-30s | 2-3s (no cold start) |
| Warm Load | 5-8s | 1-2s |
| Tab Switch | 2-3s | 0.3-0.5s |
| Filter Apply | 1-2s | 0.2-0.3s |

## 💰 Cost Impact

**Before**: ~$0-5/month (cold starts, slow performance)
**After**: ~$35-50/month (1 instance always running, fast performance)

**If cost is a concern**, use this instead:

```bash
gcloud run deploy workforce-portal \
  --source . \
  --region asia-southeast1 \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 0
```

This gives:
- Cost: ~$10-20/month
- Performance: 5s cold start, then fast
- Good for demos/low-traffic sites

## ✅ Verify Fix

After redeploying:

1. **Check it's using optimized version:**
   ```bash
   gcloud run services describe workforce-portal \
     --region asia-southeast1 \
     --format 'value(spec.template.spec.containers[0].command)'
   ```
   Should see: `streamlit run app_optimized.py`

2. **Test the site:**
   - Should load in 2-3 seconds
   - All tabs should switch instantly
   - Filters should respond in <1 second

3. **Monitor logs:**
   ```bash
   gcloud run services logs read workforce-portal \
     --region asia-southeast1 \
     --limit 20
   ```

## 🆘 Still Slow?

If still slow after redeploying:

**Increase to 4GB RAM:**
```bash
gcloud run services update workforce-portal \
  --region asia-southeast1 \
  --memory 4Gi
```

**Or test locally first:**
```bash
docker build -t test-app .
docker run -p 8080:8080 test-app
```

Visit `http://localhost:8080` - should be fast.

## 📞 Need Help?

Check the full deployment guide: `GCP_DEPLOYMENT.md`
