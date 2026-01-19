# SEO Rank Tracking Tools

A collection of Python scripts to track your website's Google rankings using different methods: Google Search Console API and SerpAPI.

## 📁 Files Overview

### 1. `google_rank.py`
Uses **Google Search Console API** to fetch official ranking data directly from Google.
- ✅ Free to use (no API costs)
- ✅ 100% accurate data from Google
- ❌ Requires Google Search Console verification
- ❌ Only shows data for verified properties
- ❌ Historical data only (not real-time)

### 2. `serp.py`
Uses **SerpAPI** to check rankings by searching Google directly (single API key).
- ✅ Real-time search results
- ✅ Can check any domain (don't need to own it)
- ✅ Shows exact SERP positions
- ❌ Costs money (uses SerpAPI credits)
- ⚠️ Limited searches per account

### 3. `serp_multiple.py`
Enhanced version of `serp.py` with **multiple API key support**.
- ✅ All benefits of `serp.py`
- ✅ Automatic failover between multiple accounts
- ✅ Extended search capacity
- ✅ Usage tracking per API key
- ❌ Still costs money (but spreads across accounts)

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Required Packages

```bash
# For google_rank.py
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# For serp.py and serp_multiple.py
pip install requests

# Install all at once (recommended)
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```

---

## 📝 Configuration & Usage

### 🔵 Option 1: Using Google Search Console (`google_rank.py`)

#### Setup Steps:

1. **Enable Google Search Console API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable "Google Search Console API"

2. **Create Service Account**
   - In Google Cloud Console → IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Download JSON key file
   - Rename it to `rank-tracker-484311-ef349be1484a.json` (or update filename in script)

3. **Add Service Account to Search Console**
   - Go to [Google Search Console](https://search.google.com/search-console)
   - Select your property
   - Settings → Users and permissions
   - Add the service account email with "Full" permissions

4. **Configure the Script**
   ```python
   SERVICE_ACCOUNT_FILE = "rank-tracker-484311-ef349be1484a.json"  # Your JSON file
   SITE_URL = "https://natro-macro.com/"  # Your website
   KEYWORDS = [
       "your keyword 1",
       "your keyword 2",
   ]
   DAYS = 7  # How many days back to check
   ```

5. **Run the Script**
   ```bash
   python google_rank.py
   ```

#### Output:
- Creates CSV file: `rank_YYYY-MM-DD.csv`
- Shows: Clicks, Impressions, CTR, Average Position

---

### 🟢 Option 2: Using SerpAPI - Single Account (`serp.py`)

#### Setup Steps:

1. **Get SerpAPI Key**
   - Sign up at [SerpAPI.com](https://serpapi.com/)
   - Get your API key from dashboard
   - Free tier: 100 searches/month

2. **Configure the Script**
   ```python
   SERPAPI_KEY = "your-api-key-here"
   YOUR_DOMAIN = "natro-macro.com"
   KEYWORDS = [
       "natro macro",
       "natro macro roblox",
   ]
   LOCATION = "India"  # or "United States", "United Kingdom", etc.
   DEVICE = "desktop"  # or "mobile"
   MAX_POSITION_TO_CHECK = 100  # How deep to search
   ```

3. **Run the Script**
   ```bash
   python serp.py
   ```

#### Output:
- Creates CSV file: `serpapi_rank_YYYY-MM-DD_HH-MM.csv`
- Shows: Exact position, searches used, status, title
- Console shows nearby results and top competitors

---

### 🟣 Option 3: Using SerpAPI - Multiple Accounts (`serp_multiple.py`)

#### Setup Steps:

1. **Get Multiple SerpAPI Keys**
   - Create 2-3 SerpAPI accounts (or buy additional keys)
   - Each account gets 100 free searches/month

2. **Configure the Script**
   ```python
   SERPAPI_KEYS = [
       "first-api-key-here",      # Account 1
       "second-api-key-here",     # Account 2
       "third-api-key-here",      # Account 3
   ]
   
   YOUR_DOMAIN = "natro-macro.com"
   KEYWORDS = [
       "natro macro",
       "natro macro roblox",
   ]
   LOCATION = "India"
   DEVICE = "desktop"
   MAX_POSITION_TO_CHECK = 100
   ```

3. **Run the Script**
   ```bash
   python serp_multiple.py
   ```

#### Features:
- Automatically switches API keys when one runs out
- Shows which key is being used in real-time
- Tracks usage per account
- Maximum search capacity (100 × number of accounts)

#### Output:
- Same CSV as `serp.py`
- **Plus:** API key usage summary showing searches used per account

---

## 📊 Understanding the Results

### Google Search Console Output (google_rank.py)
```
Keyword              | Clicks | Impressions | CTR   | Avg Position
natro macro          | 245    | 1,234       | 19.85 | 3.45
```
- **Clicks**: How many people clicked your link
- **Impressions**: How many times your link was shown
- **CTR**: Click-through rate (clicks ÷ impressions × 100)
- **Avg Position**: Average ranking over the period

### SerpAPI Output (serp.py / serp_multiple.py)
```
Keyword              | Position | Searches Used | Status | Title
natro macro          | 3        | 1             | Found  | Natro Macro - Auto...
natro macro roblox   | ?        | 10            | Not in top 100
```
- **Position**: Exact ranking (1-100)
- **Searches Used**: How many API calls were needed
- **Status**: Found / Not found
- **Title**: Your page title on Google

---

## 💰 Cost Comparison

| Method | Cost | Searches | Accuracy | Real-time |
|--------|------|----------|----------|-----------|
| Google Search Console | **FREE** | Unlimited | 100% | No (1-2 day delay) |
| SerpAPI (1 account) | **FREE** tier | 100/month | ~95% | Yes |
| SerpAPI (3 accounts) | **FREE** tier | 300/month | ~95% | Yes |
| SerpAPI Pro | $50/month | 5,000/month | ~95% | Yes |

---

## ⚠️ Important Notes

### Search Limits (SerpAPI)
- **Pages = Searches**: Each page of 10 results = 1 search
- Script stops when your site is found (saves credits)
- Example: Site at position #3 = 1 search, position #35 = 4 searches

### Rate Limiting
- Add delays between searches (already built into scripts)
- Don't run scripts too frequently (daily is fine)
- Google may show slightly different results each time

### Data Freshness
- **Google Search Console**: 1-2 days old
- **SerpAPI**: Real-time, but can vary by query

---

## 🐛 Troubleshooting

### Google Search Console Issues

**Error: "Service account not found"**
```
Solution: Make sure you added the service account email to Search Console
```

**Error: "Permission denied"**
```
Solution: Grant "Full" permissions to service account in Search Console
```

**No data returned**
```
Solution: 
- Check if keywords actually have impressions in Search Console
- Increase DAYS value (try 28 or 90)
```

### SerpAPI Issues

**Error: "Invalid API key"**
```
Solution: Double-check your API key from SerpAPI dashboard
```

**Error: "Quota exceeded"**
```
Solution: 
- Wait until next month for free tier reset
- Use serp_multiple.py with additional accounts
- Upgrade to paid plan
```

**Not finding your site**
```
Solution:
- Increase MAX_POSITION_TO_CHECK (try 200)
- Check if site actually ranks (manual Google search)
- Try different LOCATION settings
```

---

## 📅 Recommended Usage

### Daily Tracking
Use `google_rank.py` for daily tracking (free, unlimited)

### Weekly Deep Checks
Use `serp_multiple.py` weekly to verify exact positions (costs credits)

### Competitor Research
Use `serp.py` to check any domain (change YOUR_DOMAIN variable)

---

## 🔧 Customization

### Change Location
```python
LOCATION = "United States"  # or "United Kingdom", "Canada", etc.
```

### Check Mobile Rankings
```python
DEVICE = "mobile"
```

### Add More Keywords
```python
KEYWORDS = [
    "keyword 1",
    "keyword 2",
    "keyword 3",
    # Add as many as you want
]
```

### Deeper Search
```python
MAX_POSITION_TO_CHECK = 200  # Check top 200 results
```

---

## 📞 Support

- **SerpAPI Issues**: [SerpAPI Support](https://serpapi.com/support)
- **Google Search Console**: [GSC Help](https://support.google.com/webmasters)
- **Python Issues**: Make sure Python 3.7+ is installed

---

## 📜 License

These scripts are provided as-is for educational and commercial use. 

**Note**: When using SerpAPI, you agree to their [Terms of Service](https://serpapi.com/terms).

---

## ✨ Tips for Best Results

1. **Run at consistent times** for comparable data
2. **Use Google Search Console for trends**, SerpAPI for verification
3. **Track 5-10 keywords max** to stay within free tiers
4. **Check different locations** if you serve multiple regions
5. **Monitor both desktop and mobile** rankings separately

---

**Last Updated**: January 2026
