#!/usr/bin/env python3
"""
Test script for Parimatch scraper - shows how to use the scraper with different options.
"""

from parimatch_scraper import ParimatchScraper
import json

def test_with_standard_selenium():
    """Test with standard Selenium driver."""
    print("Testing with standard Selenium...")
    scraper = ParimatchScraper(headless=True, use_undetected=False)
    results = scraper.scrape_all_matches()
    return results

def test_with_undetected_chrome():
    """Test with undetected Chrome driver."""
    print("Testing with undetected Chrome...")
    scraper = ParimatchScraper(headless=True, use_undetected=True)
    results = scraper.scrape_all_matches()
    return results

def test_headless_off():
    """Test with browser visible (headless=False)."""
    print("Testing with visible browser...")
    scraper = ParimatchScraper(headless=False, use_undetected=False)
    results = scraper.scrape_all_matches()
    return results

if __name__ == "__main__":
    print("🧪 Testing Parimatch Scraper")
    print("=" * 50)
    
    # Test different configurations
    tests = [
        ("Standard Selenium", test_with_standard_selenium),
        ("Undetected Chrome", test_with_undetected_chrome),
        # Uncomment to test with visible browser
        # ("Visible Browser", test_headless_off),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔧 {test_name}")
        print("-" * 30)
        
        try:
            results = test_func()
            
            if results:
                print(f"✅ Success! Found {len(results)} matches")
                
                # Show first result as example
                if results[0].get('scores'):
                    print(f"Example: {results[0]['match']}")
                    scores = list(results[0]['scores'].items())[:3]  # First 3 scores
                    for score, odds in scores:
                        print(f"  {score}: {odds}")
                else:
                    print(f"Example: {results[0]['match']} (no odds found)")
                    
                # Save results
                filename = f"test_results_{test_name.lower().replace(' ', '_')}.json"
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"📁 Saved to {filename}")
                
                break  # Stop after first successful test
                
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n🏁 Testing completed")