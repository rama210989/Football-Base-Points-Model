#!/usr/bin/env python3
"""
Simple runner script for the Parimatch scraper.
Run this to test the scraper and see the results.
"""

import sys
import subprocess
import json
from parimatch_scraper import ParimatchScraper


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'selenium',
        'undetected_chromedriver'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nMissing packages: {missing_packages}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    
    return True


def run_scraper_test():
    """Run the scraper with error handling."""
    print("="*60)
    print("PARIMATCH PREMIER LEAGUE CORRECT SCORE ODDS SCRAPER")
    print("="*60)
    
    # Check dependencies first
    if not check_dependencies():
        print("Cannot run scraper due to missing dependencies.")
        return
    
    try:
        # Initialize scraper in headless mode
        print("\nInitializing scraper...")
        scraper = ParimatchScraper(headless=True)
        
        # Run the scraper
        print("Starting scraping process...")
        results = scraper.scrape_all_matches()
        
        if results:
            print(f"\n{'='*50}")
            print(f"SUCCESS! Found odds for {len(results)} matches")
            print(f"{'='*50}")
            
            # Display results in a formatted way
            for i, match_data in enumerate(results, 1):
                print(f"\n{i}. {match_data['match']}")
                print("-" * len(f"{i}. {match_data['match']}"))
                
                # Sort scores for better display
                sorted_scores = sorted(match_data['scores'].items(), 
                                     key=lambda x: (int(x[0].split('-')[0]), int(x[0].split('-')[1])))
                
                for score, odds in sorted_scores:
                    print(f"   {score:>5} : {odds:>6.2f}")
            
            # Save to file
            filename = 'parimatch_results.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nResults saved to '{filename}'")
            
        else:
            print("\nNo matches with correct score odds were found.")
            print("This could be due to:")
            print("- No upcoming Premier League matches")
            print("- Website structure changes")
            print("- Anti-bot detection")
            print("- Network issues")
            
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("This might be due to:")
        print("- Website being down or blocking requests")
        print("- Changes in website structure")
        print("- Chrome/ChromeDriver compatibility issues")
        print("- Network connectivity problems")


if __name__ == "__main__":
    run_scraper_test()