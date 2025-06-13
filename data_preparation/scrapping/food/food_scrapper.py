import requests


url = "https://www.visitizmir.org/en/Content/336"

# Send GET request
response = requests.get(url)

if response.status_code == 200:
    # Save the raw HTML to a file
    with open("visitizmir_full.html", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("HTML content saved successfully.")
else:
    print(f"Failed to fetch page. Status code: {response.status_code}")




