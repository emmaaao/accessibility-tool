# Tool demonstration
from src.scraper import AccessibilityScraper
from src.reporter import AccessibilityReporter

print("AI-powered accessibility analysis")

# Analyze a website
url = "https://www.hva.nl/"
print(f"\n Analyzing: {url}")

# Scrape and analyze
print("\n Step 1: Running analysis...")
scraper = AccessibilityScraper(url, headless=True, use_ai=True)
results = scraper.extract_data()

# Generate report
print("\n Step 2: Generating HTML report...")
reporter = AccessibilityReporter()
html = reporter.generate_report(results)

# Save report
filename = reporter.save_report(html)

print(f"\n COMPLETE!")
print(f" Report saved to: {filename}")
print(f" Open {filename} in your browser to view")

# Show summary
print(f"\n Summary:")
print(f"   • Technical violations: {len(results['axe_results'].get('violations', []))}")
print(f"   • Semantic issues: {len(results['week2'].get('links', []))} + {len(results['week2'].get('images', []))}")
if results.get('ai_results'):
    print(f"   • AI analyzed: Yes")