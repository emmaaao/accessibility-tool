from src.scraper import AccessibilityScraper


# Test with AI enabled
def test_ai_analysis():
    print("Testing with AI analysis enabled...")
scraper = AccessibilityScraper(
    "https://www.google.com",
    headless=True,
    use_ai=True
)

results = scraper.extract_data()

# Check AI results
if results['ai_results']:
    ai_advice = results['ai_results']['ai_advice']

    print("AI ANALYSIS RESULTS")

    # Show link analysis
    if ai_advice['links']:
        print("\n AI Link Analysis:")
        for item in ai_advice['links'][:3]:
            link = item['link']
            ai = item['ai_analysis']
            print(f"\n  Link: '{link['text']}'")
            print(f"  Accessible: {ai.get('is_accessible')}")
            print(f"  Issue: {ai.get('issue')}")
            print(f"  Recommendation: {ai.get('recommendation')}")

    # Show image analysis
    if ai_advice['images']:
        print("\n AI Image Analysis:")
        for item in ai_advice['images'][:3]:
            img = item['image']
            ai = item['ai_analysis']
            print(f"\n  Alt: '{img['alt']}'")
            print(f"  Accessible: {ai.get('is_accessible')}")
            print(f"  Recommendation: {ai.get('recommendation')}")

    print("\n AI analysis complete!")
else:
    print("\n No AI results found")