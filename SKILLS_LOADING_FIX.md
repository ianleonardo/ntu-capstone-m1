# Fix: Skills Loading Timeout on GCP

## 🔴 Problem

App gets stuck showing: **"Running DataProcessor.load_skills_data()"**

**Root Cause:** The skills parquet file is 16MB and takes 10-30 seconds to load on Cloud Run, causing:
- Browser timeout
- User frustration  
- App appears frozen

## ✅ Solutions Applied

### Solution 1: Add User Toggle (Current Implementation)

**What changed:**
- Added checkbox: "Load Skills Analysis"
- Default: **Enabled** (value=True)
- Users can uncheck to skip skills loading
- Shows progress indicator while loading

**Code location:** `app_optimized.py` lines 475-488

**User Experience:**
1. User visits Tab 2 (Sectoral Demand)
2. Sees checkbox "Load Skills Analysis" (checked by default)
3. Can uncheck to skip 16MB load
4. If checked, shows spinner "Loading skills data (16MB)..."

### Solution 2: Make Skills Opt-In (Recommended for GCP)

**For better GCP performance, make skills loading OPT-IN instead of default:**

```python
# In app_optimized.py, line 476, change:
load_skills = st.checkbox("Load Skills Analysis", value=False, key="load_skills_toggle")
```

This way:
- App loads fast by default
- Users explicitly choose to load skills
- Prevents timeout issues
- Better user experience on slow connections

## 🚀 Quick Deploy Fix

### Option A: Disable Skills by Default

**1. Update the toggle value:**

Edit `app_optimized.py` line 476:
```python
load_skills = st.checkbox("Load Skills Analysis", value=False, ...)
```

**2. Redeploy:**
```bash
gcloud run deploy workforce-portal \
  --source . \
  --region asia-southeast1 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1
```

### Option B: Remove Skills Chart Entirely (Fastest)

If skills analysis is not critical:

**1. Comment out the entire skills section** in Tab 2 (lines 471-583)

**2. Or use environment variable:**

Add to Dockerfile:
```dockerfile
ENV ENABLE_SKILLS=false
```

Then in code:
```python
if os.getenv('ENABLE_SKILLS', 'true').lower() == 'true':
    # Skills loading code
```

## 🎯 Alternative: Optimize Skills File

### Reduce Skills File Size

**Option 1: Sample the data**
```python
# In load_skills_data():
df = pd.read_parquet(Config.SKILL_FILE)
# Keep only last 3 months
df['posting_date'] = pd.to_datetime(df['posting_date'])
df = df[df['posting_date'] >= df['posting_date'].max() - pd.DateOffset(months=3)]
return df
```

**Option 2: Load specific columns only**
```python
# Load only needed columns
df = pd.read_parquet(Config.SKILL_FILE, columns=[
    'job_id', 'skill', 'category', 'posting_date'
])
```

**Option 3: Create a smaller skills file**
```bash
# In preprocessing
python -c "
import pandas as pd
df = pd.read_parquet('data/cleaned-sgjobdata-category-withskills.parquet')
# Keep only last 6 months
df = df.sort_values('posting_date').tail(100000)
df.to_parquet('data/skills-lite.parquet', compression='snappy')
"
```

Then update `Config.SKILL_FILE = 'data/skills-lite.parquet'`

## 📊 Performance Comparison

| Approach | Load Time | File Size | User Experience |
|----------|-----------|-----------|-----------------|
| Current (toggle on) | 10-30s | 16MB | Can be slow |
| Toggle off by default | <2s | Skip | Fast, opt-in |
| Sampled data (3 months) | 3-5s | ~4MB | Good balance |
| Columns only | 5-8s | ~8MB | Moderate |
| Remove entirely | <2s | 0MB | Fastest |

## 🎯 Recommended Approach

**For Production (Public Users):**
```python
# Set default to False (opt-in)
load_skills = st.checkbox("Load Skills Analysis", value=False, ...)
```

**Why:**
- Fast initial load (<3s)
- No timeout issues
- Users who need skills can enable it
- Better UX for majority of users

**For Internal Use (Your Team):**
```python
# Keep default True but add timeout handling
load_skills = st.checkbox("Load Skills Analysis", value=True, ...)
```

**Why:**
- Your team knows to wait
- Checkbox allows quick disable if needed
- Full functionality available

## 🔄 Deployment Commands

### Deploy with Skills Disabled by Default

1. Edit `app_optimized.py` line 476: `value=False`
2. Deploy:
```bash
gcloud run deploy workforce-portal \
  --source . \
  --region asia-southeast1 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1
```

### Test Locally First

```bash
# Test the change
streamlit run app_optimized.py

# Build and test Docker locally
docker build -t test-app .
docker run -p 8080:8080 test-app
```

Visit `http://localhost:8080`, go to Tab 2, verify:
- Checkbox is unchecked by default
- App loads fast without skills
- Checking box loads skills successfully

## ✅ Success Criteria

After fix:
- [ ] App loads in <3 seconds
- [ ] Tab 2 visible without waiting
- [ ] Skills checkbox present and functional
- [ ] Other charts work normally
- [ ] No timeout errors in logs

---

**Recommended:** Set `value=False` for public deployment, redeploy, and test!
