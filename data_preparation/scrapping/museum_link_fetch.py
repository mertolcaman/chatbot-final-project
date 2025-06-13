from bs4 import BeautifulSoup

base_url = "https://www.turkishmuseums.com"
all_links = []

# Loop through all saved HTML files (assuming pages 1 to 3)
for i in range(1, 4):
    filename = f"museum_page_{i}.html"
    with open(filename, "r", encoding="utf-8") as file:
        html = file.read()
    
    soup = BeautifulSoup(html, "html.parser")
    museum_links = soup.find_all("a", class_="motd")
    
    for link in museum_links:
        href = link.get("href")
        if href:
            full_url = base_url + href
            all_links.append(full_url)

# Print all extracted links
for url in all_links:
    print(url)

# Optionally save to a text file
with open("all_museum_links.txt", "w", encoding="utf-8") as f:
    for url in all_links:
        f.write(url + "\n")

print(" Saved all museum links to all_museum_links.txt")
