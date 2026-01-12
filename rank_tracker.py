from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time

YOUR_DOMAIN = "https://natromacro.com/"   # change

KEYWORDS = [
    "natro macro",
    "natro macro roblox",
    "natro macro bee swarm simulator",
    "natro macro settings",
    "how to use natro macro"
]

today = datetime.now().strftime("%Y-%m-%d")
filename = f"rank_{today}.csv"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Keyword", "Rank"])

        for keyword in KEYWORDS:
            search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
            page.goto(search_url, timeout=60000)
            time.sleep(3)

            links = page.query_selector_all("a")

            rank = 1
            found = False

            for link in links:
                href = link.get_attribute("href")
                if href and YOUR_DOMAIN in href:
                    writer.writerow([keyword, rank])
                    print(keyword, "=>", rank)
                    found = True
                    break
                rank += 1

            if not found:
                writer.writerow([keyword, "Not in Top 100"])
                print(keyword, "=> Not in Top 100")

    browser.close()

print("Saved:", filename)
