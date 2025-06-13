import requests
import time
import os
from urllib.parse import quote

# Ensure folder exists to store museum pages
os.makedirs("museum_pages", exist_ok=True)

# Load URLs from previous output
with open("all_museum_links.txt", "r", encoding="utf-8") as f:
    museum_urls = [line.strip() for line in f.readlines()]

token = "eaefc831d9a34fa18534e282c675081c103726f601e"  # Replace with your real token

# Fetch and save each museum page
for idx, url in enumerate(museum_urls, start=1):
    encoded_url = quote(url)
    scrape_url = f"http://api.scrape.do/?token={token}&url={encoded_url}"
    
    try:
        response = requests.get(scrape_url, timeout=10)
        filename = f"museum_pages/museum_{idx}.html"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f" Saved {filename}")
        time.sleep(1.5)  # polite delay between requests
    
    except Exception as e:
        print(f" Failed to fetch {url}: {e}")
