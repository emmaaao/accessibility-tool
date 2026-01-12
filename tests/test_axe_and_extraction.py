from src.scraper import AccessibilityScraper
from src.semantic_validator import classify_link


def test_axe_and_extraction():
    scraper = AccessibilityScraper("https://google.com", headless=True)
    result = scraper.extract_data()

    assert "raw_elements" in result
    assert "semantic_elements" in result
    assert "axe_results" in result

    raw = result["raw_elements"]
    assert "links" in raw
    assert "images" in raw
    assert "text_blocks" in raw

    semantic = result["semantic_elements"]
    for category in ["links", "images", "text_blocks"]:
        for item in semantic[category]:
            assert "semantic_role" in item
            assert "confidence" in item
            assert 0.0 <= item["confidence"] <= 1.0


def test_multilingual_navigation():
    nl = {"text": "Over ons", "href": "/about"}

    assert classify_link(nl)[0] == "navigation"

