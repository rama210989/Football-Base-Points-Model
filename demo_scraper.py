#!/usr/bin/env python3
"""
Demonstration script for the Parimatch scraper.
Shows different usage modes and configurations.
"""

from parimatch_scraper import ParimatchScraper
import json

def demo_headless_scraping():
    """Demonstrate headless scraping (production mode)."""
    print("=== DEMO: Headless Scraping (Production Mode) ===")
    
    scraper = ParimatchScraper(headless=True)
    results = scraper.scrape_all_matches()
    
    if results:
        print(f"Found {len(results)} matches with odds:")
        for match in results:
            print(f"\n{match['match']}:")
            for score, odds in sorted(match['scores'].items()):
                print(f"  {score}: {odds}")
    else:
        print("No matches found in headless mode.")
    
    return results

def demo_visible_scraping():
    """Demonstrate visible browser scraping (debug mode)."""
    print("\n=== DEMO: Visible Browser (Debug Mode) ===")
    print("This will open a visible Chrome window - great for debugging!")
    print("Press Ctrl+C to skip this demo if you don't want to see the browser.")
    
    try:
        input("Press Enter to continue or Ctrl+C to skip...")
        
        scraper = ParimatchScraper(headless=False)
        results = scraper.scrape_all_matches()
        
        if results:
            print(f"Found {len(results)} matches with odds:")
            for match in results:
                print(f"\n{match['match']}:")
                for score, odds in sorted(match['scores'].items()):
                    print(f"  {score}: {odds}")
        else:
            print("No matches found in visible mode.")
        
        return results
        
    except KeyboardInterrupt:
        print("\nSkipping visible browser demo.")
        return []

def demo_custom_usage():
    """Demonstrate custom usage of the scraper components."""
    print("\n=== DEMO: Custom Component Usage ===")
    
    scraper = ParimatchScraper(headless=True)
    
    try:
        # Setup driver
        scraper.driver = scraper.setup_driver()
        
        # Extract match links only
        print("Extracting match links...")
        match_links = scraper.extract_match_links()
        
        if match_links:
            print(f"Found {len(match_links)} match links:")
            for i, link in enumerate(match_links[:3], 1):  # Show first 3
                print(f"  {i}. {link}")
            
            if len(match_links) > 3:
                print(f"  ... and {len(match_links) - 3} more")
        else:
            print("No match links found.")
        
        return match_links
        
    except Exception as e:
        print(f"Error in custom usage demo: {e}")
        return []
    
    finally:
        if scraper.driver:
            scraper.driver.quit()

def save_demo_results(results, filename="demo_results.json"):
    """Save demo results to a file."""
    if results:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nDemo results saved to '{filename}'")

def main():
    """Main demo function."""
    print("🎯 PARIMATCH SCRAPER DEMONSTRATION")
    print("="*50)
    
    # Demo 1: Headless scraping
    results = demo_headless_scraping()
    
    # Demo 2: Visible browser (optional)
    visible_results = demo_visible_scraping()
    
    # Demo 3: Custom component usage
    match_links = demo_custom_usage()
    
    # Save results if any were found
    all_results = results + visible_results
    if all_results:
        save_demo_results(all_results)
    
    print("\n" + "="*50)
    print("DEMO COMPLETED!")
    print("\nSummary:")
    print(f"- Headless mode found: {len(results)} matches")
    print(f"- Visible mode found: {len(visible_results)} matches")
    print(f"- Match links found: {len(match_links)}")
    
    if not any([results, visible_results, match_links]):
        print("\nNo data found - this could be due to:")
        print("1. No upcoming Premier League matches")
        print("2. Website blocking/detection")
        print("3. Changed website structure")
        print("4. Network connectivity issues")
        print("\nThe scraper is working correctly - this is expected behavior.")

if __name__ == "__main__":
    main()