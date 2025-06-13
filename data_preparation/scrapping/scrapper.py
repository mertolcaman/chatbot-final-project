import requests
import urllib.parse

token = "eaefc831d9a34fa18534e282c675081c103726f601e"

# List of URLs to scrape
target_urls = [
    "https://www.turkishmuseums.com/museums?s=&b=&i=35&m=&o=&l=4&p=1",
    "https://www.turkishmuseums.com/museums?s=&b=&i=35&m=&o=&l=4&p=2",
    "https://www.turkishmuseums.com/museums?s=&b=&i=35&m=&o=&l=4&p=3"
]

# Loop through each URL and save the HTML
for idx, target_url in enumerate(target_urls, start=1):
    encoded_url = urllib.parse.quote(target_url)
    url = f"http://api.scrape.do/?token={token}&url={encoded_url}"
    
    response = requests.get(url)
    
    filename = f"museum_page_{idx}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(response.text)
    
    print(f"Saved {filename}")
