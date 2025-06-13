from bs4 import BeautifulSoup

# Load your saved HTML file
with open("blog.corendonairlines.com_sunny-destinations_the-most-beautiful-beaches-in-izmir-a-guide-to-beaches-in-izmir.html", "r", encoding="utf-8") as file:
    html = file.read()

soup = BeautifulSoup(html, "html.parser")

output_lines = []

# 1. Title
title_tag = soup.find("h1", class_="text-style text-style--h2")
if title_tag:
    output_lines.append(f"Title: {title_tag.get_text(strip=True)}\n")

# 2. Meta info
meta_items = soup.select("ul.page__meta li span.page__meta-item-label")
for item in meta_items:
    output_lines.append(item.get_text(strip=True))

output_lines.append("")  # Blank line

# 3. Intro paragraph
entry_div = soup.find("div", class_="entry")
if entry_div:
    first_paragraph = entry_div.find("p")
    if first_paragraph:
        output_lines.append(first_paragraph.get_text(strip=True))
        output_lines.append("")

# 4. General beach region names
region_beaches = soup.select("ul.list--dotted li span")
if region_beaches:
    output_lines.append("Beach Regions:")
    for li in region_beaches:
        output_lines.append(f"- {li.get_text(strip=True)}")
    output_lines.append("")

# 5. Specific beach names (like Ilıca Beach and Altınkum Beach)
specific_beaches = soup.select("li.list__item[aria-level='2'] b")
if specific_beaches:
    output_lines.append("Specific Beaches:")
    for b in specific_beaches:
        output_lines.append(f"- {b.get_text(strip=True)}")

# 6. Save to text file
with open("izmir_beaches_full_summary.txt", "w", encoding="utf-8") as out_file:
    out_file.write("\n".join(output_lines))

print("Full beach summary saved to 'izmir_beaches_full_summary.txt'")
