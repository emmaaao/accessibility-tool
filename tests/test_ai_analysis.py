from src.scraper import AccessibilityScraper

def test_analysis_structure():
    scraper = AccessibilityScraper("https://google.com", headless=True)
    result = scraper.extract_data()

    week2 = result["week2"]

    # Required categories
    assert "readability" in week2
    assert "images" in week2
    assert "links" in week2

    # Readability results
    for item in week2["readability"]:
        assert "level" in item
        assert item["level"] in ["easy", "medium", "hard"]

    # Image analysis results
    for item in week2["images"]:
        assert "issue" in item
        assert "severity" in item

    # Link analysis results
    for item in week2["links"]:
        assert "issue" in item
        assert "severity" in item
