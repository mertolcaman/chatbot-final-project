from bs4 import BeautifulSoup

# Load the HTML file
with open("visitizmir_full.html", "r", encoding="utf-8") as file:
    html = file.read()

# Parse HTML
soup = BeautifulSoup(html, "html.parser")

foods = []

# Extract food names and descriptions
for p in soup.find_all("p", style="text-align: justify;"):
    strong_tag = p.find("strong")
    if strong_tag:
        name = strong_tag.text.strip()
        strong_tag.extract()  # Remove name from description
        description = p.get_text(separator=" ", strip=True)
        foods.append({"name": name, "description": description})

# Write the content to a text file
with open("izmir_foods.txt", "w", encoding="utf-8") as txt_file:
    for food in foods:
        txt_file.write(f"Name: {food['name']}\n")
        txt_file.write(f"Description: {food['description']}\n")
        txt_file.write("\n" + "-"*50 + "\n\n")

print("Food content successfully saved to 'izmir_foods.txt'")
