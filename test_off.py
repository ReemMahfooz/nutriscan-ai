import requests

barcode = "3017624010701"

url = f"https://world.openfoodfacts.org/api/v3/product/{barcode}.json"

headers = {
    "User-Agent": "NutriScanAI/1.0 (contact@example.com)"
}

response = requests.get(
    url,
    headers=headers,
    timeout=10
)

print("HTTP status:", response.status_code)

data = response.json()

print("API status:", data.get("status"))

product = data.get("product", {})

print("Product:", product.get("product_name"))
print("Ingredients:", product.get("ingredients_text"))
print("Nutrition:", product.get("nutriments"))