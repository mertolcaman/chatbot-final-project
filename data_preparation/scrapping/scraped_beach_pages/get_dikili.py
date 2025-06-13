from bs4 import BeautifulSoup

# Load the local HTML file
with open("www.visitizmir.org_en_Icerik_218.html", "r", encoding="utf-8") as file:
    html = file.read()

# Parse HTML
soup = BeautifulSoup(html, "html.parser")

# Prepare text content
output_lines = []

# Extract the title
title = soup.find("h1")
if title:
    output_lines.append(f"{title.get_text(strip=True)}\n")

# Extract paragraphs in the content area
content_div = soup.find("div", class_="content")
if content_div:
    paragraphs = content_div.find_all("p")
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            output_lines.append(text)

# Save to a .txt file
with open("dikili_bays.txt", "w", encoding="utf-8") as txt_file:
    txt_file.write("\n\n".join(output_lines))

print("Content saved to 'dikili_bays.txt'")