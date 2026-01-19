import requests
import time
import csv
from datetime import datetime

# ---------------- CONFIG ----------------
SERPAPI_KEY = "f34768ed553f15c26f939ffa87a60f534163d3b1913fa9f72c1630e45344a8bc"
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
MAX_POSITION_TO_CHECK = 100  # Will paginate up to this position
RESULTS_PER_PAGE = 10  # Google now defaults to 10 results per page (ignores num=100)
OUTPUT_FILE = f"serpapi_rank_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5
# ----------------------------------------

def search_google_serpapi_page(keyword, api_key, start=0, location="India", device="desktop"):
    """
    Search Google using SerpAPI with pagination
    """
    url = "https://serpapi.com/search"
    
    params = {
        "q": keyword,
        "location": location,
        "hl": "en",
        "gl": "in",
        "google_domain": "google.co.in",
        "api_key": api_key,
        "start": start,  # Pagination offset
        "num": RESULTS_PER_PAGE,
        "device": device
    }
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
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

def search_until_found(keyword, domain, api_key, max_position=100, location="India", device="desktop"):
    """
    Keep searching pages until domain is found or max_position is reached
    """
    all_results = []
    position = None
    pages_searched = 0
    
    for start in range(0, max_position, RESULTS_PER_PAGE):
        pages_searched += 1
        current_page = (start // RESULTS_PER_PAGE) + 1
        
        print(f"    Checking positions {start + 1}-{min(start + RESULTS_PER_PAGE, max_position)}... (page {current_page})")
        
        data = search_google_serpapi_page(keyword, api_key, start, location, device)
        
        if not data:
            return position, all_results, f"Failed to get page {current_page}", pages_searched
        
        if "error" in data:
            return position, all_results, f"API Error: {data['error']}", pages_searched
        
        organic_results = data.get("organic_results", [])
        
        if not organic_results:
            # No more results
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
            
            # Check if this is your domain
            if domain.lower() in link.lower():
                if position is None:
                    position = actual_position
                    print(f"    FOUND at position #{position}!")
                    return position, all_results, "Found", pages_searched
        
        # Don't search next page if we already found it or reached the end
        if position or len(organic_results) < RESULTS_PER_PAGE:
            break
        
        # Small delay between pages
        time.sleep(2)
    
    status = f"Not found in top {len(all_results)} results"
    return position, all_results, status, pages_searched

print("=" * 80)
print(" DEEP RANK CHECKER - SerpAPI with Pagination")
print("=" * 80)
print(f"Domain: {YOUR_DOMAIN}")
print(f"Location: {LOCATION} | Device: {DEVICE.upper()}")
print(f"Max depth: Top {MAX_POSITION_TO_CHECK} results")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Check account
print("\n Checking SerpAPI account...")
account_url = f"https://serpapi.com/account?api_key={SERPAPI_KEY}"
try:
    account_response = requests.get(account_url, timeout=10)
    account_data = account_response.json()
    
    searches_left = account_data.get("plan_searches_left", "?")
    total_searches = account_data.get("total_searches_left", "?")
    
    print(f" Account active")
    print(f"   Searches available: {searches_left}")
    
    # Estimate searches needed
    max_pages = MAX_POSITION_TO_CHECK // RESULTS_PER_PAGE
    estimated_searches = len(KEYWORDS) * max_pages
    print(f"     This could use up to {estimated_searches} searches")
    print(f"       ({len(KEYWORDS)} keywords × up to {max_pages} pages each)")
    print(f"    Script stops as soon as your site is found on any page!")
    print(f"\n   ℹ  Note: Google limits results to ~10 per page, so we use pagination")
except Exception as e:
    print(f"  Could not check account: {e}")

input("\nPress ENTER to continue or Ctrl+C to cancel...")

print("\n" + "=" * 80)

results_data = []
total_searches_used = 0

for idx, keyword in enumerate(KEYWORDS, 1):
    print(f"\n [{idx}/{len(KEYWORDS)}] Searching: '{keyword}'")
    print("-" * 80)
    
    position, all_results, status, pages_used = search_until_found(
        keyword, YOUR_DOMAIN, SERPAPI_KEY, MAX_POSITION_TO_CHECK, LOCATION, DEVICE
    )
    
    total_searches_used += pages_used
    
    if position:
        print(f" FOUND at position #{position} (used {pages_used} searches)")
        
        your_result = all_results[position - 1]
        print(f"\n    Your listing:")
        print(f"      Title: {your_result['title']}")
        print(f"      URL: {your_result['link']}")
        print(f"      Snippet: {your_result['snippet'][:80]}...")
        
        # Show context
        print(f"\n    Nearby results:")
        start = max(0, position - 3)
        end = min(len(all_results), position + 2)
        
        for result in all_results[start:end]:
            pos = result['position']
            marker = "" if pos == position else "  "
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
        print(f" NOT FOUND in top {len(all_results)} results (used {pages_used} searches)")
        
        if all_results and len(all_results) >= 3:
            print(f"\n   Top 3 results:")
            for result in all_results[:3]:
                title = result['title'][:60] + "..." if len(result['title']) > 60 else result['title']
                print(f"      #{result['position']} - {title}")
        
        results_data.append([
            keyword,
            "?",
            pages_used,
            f"Not in top {len(all_results)}",
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
        print(f" #{position:2} - {keyword} ({searches} searches)")
    else:
        print(f"❌  ?? - {keyword} ({searches} searches)")

print(f"\n TOTAL SEARCHES USED: {total_searches_used}")
print(f"   Remaining: ~{searches_left - total_searches_used if isinstance(searches_left, int) else '?'}")
print("\n TIP: Each page = 1 search. Script stops when your site is found!")
print("   Keywords ranking in top 10 = 1 search each")
print("   Keywords ranking 11-20 = 2 searches each, etc.")
