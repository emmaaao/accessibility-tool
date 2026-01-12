#Simple test script to verify scraper functionality
from src.scraper import AccessibilityScraper
import json


# TEST_URL = "https://www.w3.org/WAI/demos/bad/"
# TEST_URL = "https://www.example.com"
# TEST_URL = "https://www.google.com"

scraper = AccessibilityScraper("https://www.google.com", headless=True)
result = scraper.extract_data()

print(json.dumps(result["semantic_elements"]["links"][:5], indent=2))
print(json.dumps(result["semantic_elements"]["images"][:5], indent=2))

assert "raw_elements" in result
assert "semantic_elements" in result
assert "axe_results" in result