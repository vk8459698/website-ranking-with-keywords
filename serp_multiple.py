import requests
import time
import csv
from datetime import datetime

# ---------------- CONFIG ----------------
# Add multiple API keys - script will automatically switch when one runs out
SERPAPI_KEYS = [
    "f34768ed553f15c26f939ffa87a60f534163d3b1913fa9f72c1630e45344a8bc",  # Account 1
    "",  # Account 2 - Add your second API key here
    "",  # Account 3 - Add your third API key here
]

YOUR_DOMAIN = "natro-macro.com"
KEYWORDS = [
    "natro macro",
    "natro macro roblox",
    "natro macro bee swarm simulator",
    "natro macro settings",
    "how to use natro macro"
]
LOCATION = "India"
DEVICE = "desktop"
MAX_POSITION_TO_CHECK = 100
RESULTS_PER_PAGE = 10
OUTPUT_FILE = f"serpapi_rank_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5
# ----------------------------------------

class APIKeyManager:
    """Manages multiple API keys with automatic failover"""
    
    def __init__(self, api_keys):
        # Filter out empty keys
        self.api_keys = [key.strip() for key in api_keys if key.strip()]
        self.current_index = 0
        self.key_stats = {key: {"used": 0, "remaining": "?", "failed": False} for key in self.api_keys}
        
        if not self.api_keys:
            raise ValueError("No valid API keys provided!")
    
    def get_current_key(self):
        """Get the current active API key"""
        if self.current_index >= len(self.api_keys):
            return None
        return self.api_keys[self.current_index]
    
    def switch_to_next_key(self):
        """Switch to the next available API key"""
        self.key_stats[self.api_keys[self.current_index]]["failed"] = True
        self.current_index += 1
        
        if self.current_index < len(self.api_keys):
            new_key = self.get_current_key()
            print(f"\n   Switching to API key #{self.current_index + 1}...")
            return True
        else:
            print(f"\n   All API keys exhausted!")
            return False
    
    def record_usage(self, key):
        """Record that a search was used"""
        if key in self.key_stats:
            self.key_stats[key]["used"] += 1
    
    def update_remaining(self, key, remaining):
        """Update remaining searches for a key"""
        if key in self.key_stats:
            self.key_stats[key]["remaining"] = remaining
    
    def get_stats(self):
        """Get usage statistics for all keys"""
        return self.key_stats
    
    def get_active_key_number(self):
        """Get the number of the current active key"""
        return self.current_index + 1
    
    def has_available_keys(self):
        """Check if there are any keys left to use"""
        return self.current_index < len(self.api_keys)

def check_account_status(api_key):
    """Check remaining searches for an API key"""
    account_url = f"https://serpapi.com/account?api_key={api_key}"
    try:
        response = requests.get(account_url, timeout=10)
        data = response.json()
        
        if "error" in data:
            return None, data["error"]
        
        searches_left = data.get("plan_searches_left", "?")
        return searches_left, None
    except Exception as e:
        return None, str(e)

def search_google_serpapi_page(keyword, api_key, start=0, location="India", device="desktop"):
    """Search Google using SerpAPI with pagination"""
    url = "https://serpapi.com/search"
    
    params = {
        "q": keyword,
        "location": location,
        "hl": "en",
        "gl": "in",
        "google_domain": "google.co.in",
        "api_key": api_key,
        "start": start,
        "num": RESULTS_PER_PAGE,
        "device": device
    }
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Check for API limit errors
            if "error" in data:
                error_msg = data["error"]
                if "limit" in error_msg.lower() or "quota" in error_msg.lower():
                    return {"quota_exceeded": True, "error": error_msg}
            
            return data
        except requests.exceptions.Timeout:
            if attempt < RETRY_ATTEMPTS - 1:
                print(f"     Timeout, retrying in {RETRY_DELAY}s... (attempt {attempt + 2}/{RETRY_ATTEMPTS})")
                time.sleep(RETRY_DELAY)
            else:
                print(f"    Failed after {RETRY_ATTEMPTS} attempts")
                return None
        except Exception as e:
            print(f"    API Error: {e}")
            return None
    
    return None

def search_until_found(keyword, domain, key_manager, max_position=100, location="India", device="desktop"):
    """Keep searching pages until domain is found or max_position is reached"""
    all_results = []
    position = None
    pages_searched = 0
    
    for start in range(0, max_position, RESULTS_PER_PAGE):
        pages_searched += 1
        current_page = (start // RESULTS_PER_PAGE) + 1
        
        print(f"    Checking positions {start + 1}-{min(start + RESULTS_PER_PAGE, max_position)}... (page {current_page}) [Key #{key_manager.get_active_key_number()}]")
        
        # Get current API key
        api_key = key_manager.get_current_key()
        if not api_key:
            return position, all_results, "All API keys exhausted", pages_searched
        
        data = search_google_serpapi_page(keyword, api_key, start, location, device)
        
        if not data:
            return position, all_results, f"Failed to get page {current_page}", pages_searched
        
        # Check for quota exceeded
        if isinstance(data, dict) and data.get("quota_exceeded"):
            print(f"    API key #{key_manager.get_active_key_number()} quota exceeded!")
            
            if key_manager.switch_to_next_key():
                # Retry this page with new key
                api_key = key_manager.get_current_key()
                data = search_google_serpapi_page(keyword, api_key, start, location, device)
                
                if not data or data.get("quota_exceeded"):
                    return position, all_results, "All API keys exhausted", pages_searched
            else:
                return position, all_results, "All API keys exhausted", pages_searched
        
        if "error" in data and not data.get("quota_exceeded"):
            return position, all_results, f"API Error: {data['error']}", pages_searched
        
        # Record successful usage
        key_manager.record_usage(api_key)
        
        organic_results = data.get("organic_results", [])
        
        if not organic_results:
            break
        
        for i, result in enumerate(organic_results):
            actual_position = start + i + 1
            link = result.get("link", "")
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            all_results.append({
                "position": actual_position,
                "title": title,
                "link": link,
                "snippet": snippet
            })
            
            if domain.lower() in link.lower():
                if position is None:
                    position = actual_position
                    print(f"    FOUND at position #{position}!")
                    return position, all_results, "Found", pages_searched
        
        if position or len(organic_results) < RESULTS_PER_PAGE:
            break
        
        time.sleep(2)
    
    status = f"Not found in top {len(all_results)} results"
    return position, all_results, status, pages_searched

# Main execution
print("=" * 80)
print(" MULTI-ACCOUNT RANK CHECKER - SerpAPI with Auto-Failover")
print("=" * 80)
print(f"Domain: {YOUR_DOMAIN}")
print(f"Location: {LOCATION} | Device: {DEVICE.upper()}")
print(f"Max depth: Top {MAX_POSITION_TO_CHECK} results")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Initialize API key manager
try:
    key_manager = APIKeyManager(SERPAPI_KEYS)
    print(f"\n Loaded {len(key_manager.api_keys)} API key(s)")
except ValueError as e:
    print(f"\n ERROR: {e}")
    exit(1)

# Check all accounts
print("\n Checking SerpAPI accounts...")
for i, key in enumerate(key_manager.api_keys, 1):
    searches_left, error = check_account_status(key)
    
    if error:
        print(f"   Account {i}: Error - {error}")
        key_manager.key_stats[key]["remaining"] = "Error"
    else:
        print(f"   Account {i}: {searches_left} searches available")
        key_manager.update_remaining(key, searches_left)

# Estimate searches needed
max_pages = MAX_POSITION_TO_CHECK // RESULTS_PER_PAGE
estimated_searches = len(KEYWORDS) * max_pages
print(f"\n Estimated max searches needed: {estimated_searches}")
print(f"   ({len(KEYWORDS)} keywords × up to {max_pages} pages each)")
print(f"   Script stops as soon as your site is found on any page!")

input("\nPress ENTER to continue or Ctrl+C to cancel...")

print("\n" + "=" * 80)

results_data = []
total_searches_used = 0

for idx, keyword in enumerate(KEYWORDS, 1):
    if not key_manager.has_available_keys():
        print(f"\n All API keys exhausted! Stopping at keyword {idx}/{len(KEYWORDS)}")
        break
    
    print(f"\n [{idx}/{len(KEYWORDS)}] Searching: '{keyword}' (Using API Key #{key_manager.get_active_key_number()})")
    print("-" * 80)
    
    position, all_results, status, pages_used = search_until_found(
        keyword, YOUR_DOMAIN, key_manager, MAX_POSITION_TO_CHECK, LOCATION, DEVICE
    )
    
    total_searches_used += pages_used
    
    if position:
        print(f" FOUND at position #{position} (used {pages_used} searches)")
        
        your_result = all_results[position - 1]
        print(f"\n    Your listing:")
        print(f"      Title: {your_result['title']}")
        print(f"      URL: {your_result['link']}")
        print(f"      Snippet: {your_result['snippet'][:80]}...")
        
        print(f"\n    Nearby results:")
        start = max(0, position - 3)
        end = min(len(all_results), position + 2)
        
        for result in all_results[start:end]:
            pos = result['position']
            marker = "➤" if pos == position else "  "
            title = result['title'][:60] + "..." if len(result['title']) > 60 else result['title']
            print(f"   {marker} #{pos:2d} - {title}")
        
        results_data.append([
            keyword, 
            position,
            pages_used,
            "Found",
            your_result['title'][:50],
            datetime.now().strftime('%H:%M:%S')
        ])
    else:
        print(f" {status} (used {pages_used} searches)")
        
        if all_results and len(all_results) >= 3:
            print(f"\n   Top 3 results:")
            for result in all_results[:3]:
                title = result['title'][:60] + "..." if len(result['title']) > 60 else result['title']
                print(f"      #{result['position']} - {title}")
        
        results_data.append([
            keyword,
            "?",
            pages_used,
            status,
            "",
            datetime.now().strftime('%H:%M:%S')
        ])
    
    if idx < len(KEYWORDS):
        print("    Waiting 3 seconds before next keyword...")
        time.sleep(3)

# Save results
print("\n" + "=" * 80)
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Keyword", "Position", "Searches Used", "Status", "Title", "Time"])
    writer.writerows(results_data)

print(f" Saved: {OUTPUT_FILE}")
print("=" * 80)

print("\n SUMMARY:")
print("-" * 80)
for keyword, position, searches, status, title, check_time in results_data:
    if position != "?":
        print(f" ✓ #{position:2} - {keyword} ({searches} searches)")
    else:
        print(f" ✗ ?? - {keyword} ({searches} searches)")

print(f"\n API KEY USAGE:")
print("-" * 80)
for i, (key, stats) in enumerate(key_manager.get_stats().items(), 1):
    status = "EXHAUSTED" if stats["failed"] else "Active"
    key_preview = key[:20] + "..." if len(key) > 20 else key
    print(f"   Key #{i} ({key_preview}): {stats['used']} used, ~{stats['remaining']} remaining [{status}]")

print(f"\n TOTAL SEARCHES USED: {total_searches_used}")
print("\n TIP: Script automatically switches API keys when one runs out!")
print("   Add more keys to SERPAPI_KEYS list for extended searching")
