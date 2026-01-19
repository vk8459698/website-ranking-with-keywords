from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta
import csv

# ---------------- CONFIG ----------------
SERVICE_ACCOUNT_FILE = "rank-tracker-484311-ef349be1484a.json"
SITE_URL = "https://natro-macro.com/"
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
KEYWORDS = [
    "natro macro",
    "natro macro roblox",
    "natro macro bee swarm simulator",
    "natro macro settings",
    "how to use natro macro"
]
DAYS = 7  # lookback period for data
OUTPUT_FILE = f"rank_{datetime.now().strftime('%Y-%m-%d')}.csv"
# ----------------------------------------

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('searchconsole', 'v1', credentials=credentials)

end_date = datetime.now().date()
start_date = end_date - timedelta(days=DAYS)

# Open CSV file
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Keyword", "Clicks", "Impressions", "CTR", "Average Position"])

    for keyword in KEYWORDS:
        request = {
            "startDate": str(start_date),
            "endDate": str(end_date),
            "dimensions": ["query"],
            "dimensionFilterGroups": [{
                "filters": [{
                    "dimension": "query",
                    "expression": keyword
                }]
            }],
            "rowLimit": 1
        }

        response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
        rows = response.get('rows', [])

        if rows:
            row = rows[0]
            writer.writerow([
                keyword,
                row.get('clicks', 0),
                row.get('impressions', 0),
                round(row.get('ctr', 0)*100, 2),
                round(row.get('position', 0), 2)
            ])
            print(f"{keyword} => Position: {row.get('position', 0)}, Clicks: {row.get('clicks',0)}")
        else:
            writer.writerow([keyword, 0, 0, 0, "?"])
            print(f"{keyword} => No data")

print("Saved:", OUTPUT_FILE)
