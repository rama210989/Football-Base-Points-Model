#!/usr/bin/env python3
"""
Parimatch Premier League Correct Score Odds Scraper - Google Colab Version (FIXED)

This script scrapes REAL correct score odds for upcoming Premier League matches 
from Parimatch. No fake data generation - only real odds from the actual website.

Instructions for Google Colab:
1. Run the installation code first  
2. Run this main script
"""

import json
import time
import re
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

def install_dependencies():
    """Install required packages in Google Colab"""
    print("Installing required packages...")
    import subprocess
    import sys
    
    packages = ['selenium', 'webdriver-manager']
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed")
        except:
            print(f"✗ Failed to install {package}")

def setup_chrome_colab():
    """Setup Chrome for Google Colab environment"""
    print("Setting up Chrome for Colab...")
    import subprocess
    
    # Install Chrome
    subprocess.run(['apt-get', 'update'], capture_output=True)
    subprocess.run(['apt-get', 'install', '-y', 'chromium-browser'], capture_output=True)
    
    # Install ChromeDriver
    subprocess.run(['apt-get', 'install', '-y', 'chromium-chromedriver'], capture_output=True)
    
    print("Chrome setup complete!")

class ParimatchScraper:
    def __init__(self, debug: bool = True):
        """Initialize the scraper with debug mode"""
        self.base_url = "https://parimatchglobal.com"
        self.premier_league_url = "https://parimatchglobal.com/en/football/premier-league-7f5506e872d14928adf0613efa509494/prematch"
        self.driver = None
        self.debug = debug
        
    def setup_driver(self):
        """Setup Chrome driver for Colab environment"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        print("🚀 Setting up Chrome driver...")
        
        options = Options()
        
        # Colab specific options
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Anti-detection options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            # Try system chromedriver first
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
        except:
            try:
                # Fallback to webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except:
                print("❌ Failed to setup Chrome driver!")
                raise
        
        # Remove webdriver signatures
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome driver setup successful!")
        return driver
    
    def debug_page(self, description=""):
        """Debug what's actually on the page"""
        if not self.debug:
            return
            
        print(f"\n=== DEBUG: {description} ===")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Check for common elements
        from selenium.webdriver.common.by import By
        
        # Look for any links
        links = self.driver.find_elements(By.TAG_NAME, "a")
        print(f"Total links found: {len(links)}")
        
        # Look for match-related content
        match_indicators = [
            "event", "match", "fixture", "premier", "league", 
            "liverpool", "arsenal", "chelsea", "manchester", "tottenham"
        ]
        
        for indicator in match_indicators:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{indicator}')]")
            if elements:
                print(f"Found {len(elements)} elements containing '{indicator}'")
                if self.debug and len(elements) <= 5:
                    for elem in elements[:3]:
                        try:
                            text = elem.text.strip()[:100]
                            if text:
                                print(f"  - {text}...")
                        except:
                            pass
        
        # Look for any upcoming fixtures/events
        print(f"Page source length: {len(self.driver.page_source)} characters")
        
    def find_match_links(self) -> List[str]:
        """Find real match links from Parimatch - NO FAKE DATA"""
        print("🔍 Looking for Premier League matches...")
        
        try:
            self.driver.get(self.premier_league_url)
            time.sleep(8)  # Wait for page load
            
            self.debug_page("Premier League page loaded")
            
            # Scroll to load content
            print("📜 Scrolling to load all content...")
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Try different selectors for match links
            selectors = [
                "a[href*='/en/events/']",
                "a[href*='/events/']", 
                "a[href*='/football/']",
                "a[href*='match']",
                ".event a",
                ".match a",
                ".fixture a",
                "[data-testid*='event'] a",
                "[data-testid*='match'] a"
            ]
            
            match_links = []
            
            print("🔎 Searching for match links...")
            
            for selector in selectors:
                try:
                    from selenium.webdriver.common.by import By
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if self.debug:
                        print(f"Selector '{selector}': found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            text = element.text.strip()
                            
                            if href and ('/events/' in href or '/football/' in href):
                                full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                                
                                # Check if it looks like a Premier League match
                                if ('premier-league' in full_url.lower() or 
                                    any(team in text.lower() for team in ['liverpool', 'arsenal', 'chelsea', 'manchester', 'tottenham', 'city', 'united']) or
                                    any(team in href.lower() for team in ['premier', 'league'])):
                                    
                                    if full_url not in match_links:
                                        match_links.append(full_url)
                                        if self.debug:
                                            print(f"✅ Found match: {text[:50]}... -> {full_url[:80]}...")
                        except Exception as e:
                            if self.debug:
                                print(f"Error processing element: {e}")
                            continue
                    
                    if match_links:
                        break
                        
                except Exception as e:
                    if self.debug:
                        print(f"Error with selector '{selector}': {e}")
                    continue
            
            if not match_links:
                print("❌ No match links found with CSS selectors. Trying alternative approach...")
                
                # Alternative: search page source for match patterns
                page_source = self.driver.page_source.lower()
                
                # Look for Premier League team names
                pl_teams = [
                    'liverpool', 'arsenal', 'chelsea', 'manchester city', 'manchester united',
                    'tottenham', 'aston villa', 'newcastle', 'brighton', 'west ham',
                    'crystal palace', 'bournemouth', 'fulham', 'brentford', 'wolves',
                    'everton', 'nottingham forest', 'leicester', 'leeds', 'southampton'
                ]
                
                teams_found = [team for team in pl_teams if team in page_source]
                
                if teams_found:
                    print(f"🏆 Found Premier League teams on page: {teams_found[:5]}...")
                    
                    # Try to find links near team names
                    from selenium.webdriver.common.by import By
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip().lower()
                            
                            if href and any(team in text for team in teams_found[:3]):
                                full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                                if full_url not in match_links:
                                    match_links.append(full_url)
                                    print(f"✅ Found team link: {text[:50]}...")
                        except:
                            continue
                
                if not match_links:
                    print("❌ Still no matches found. Checking if page loaded correctly...")
                    print(f"Page title: {self.driver.title}")
                    print(f"URL: {self.driver.current_url}")
                    
                    # Check for common blocking patterns
                    if "blocked" in page_source or "captcha" in page_source or "robot" in page_source:
                        print("⚠️ Page might be blocked or showing captcha")
                    elif len(page_source) < 10000:
                        print("⚠️ Page seems too small - might not have loaded properly")
                    else:
                        print("⚠️ Page loaded but no Premier League matches found")
                        print("This could mean:")
                        print("  - No upcoming Premier League matches today")
                        print("  - Site structure has changed")
                        print("  - Different URL needed")
                        print("  - Site is blocking automated access")
            
            print(f"📊 Total match links found: {len(match_links)}")
            return match_links[:10]  # Limit for testing
            
        except Exception as e:
            print(f"❌ Error extracting match links: {e}")
            return []
    
    def get_team_names(self, match_url: str) -> str:
        """Extract team names from match page"""
        try:
            from selenium.webdriver.common.by import By
            
            # Try multiple selectors
            team_selectors = [
                ".teams .team", ".team-name", ".participant",
                "h1", ".event-header", ".match-header",
                "[data-testid*='team']", ".competitor"
            ]
            
            teams = []
            for selector in team_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 2:
                        teams = [elem.text.strip() for elem in elements[:2] if elem.text.strip()]
                        if len(teams) == 2:
                            break
                except:
                    continue
            
            if len(teams) == 2:
                return f"{teams[0]} vs {teams[1]}"
            
            # Fallback: try page title
            title = self.driver.title
            if 'vs' in title or ' v ' in title:
                return title.split('|')[0].strip()
            
            return "Match Teams Unknown"
            
        except Exception as e:
            print(f"Error extracting team names: {e}")
            return "Match Teams Unknown"
    
    def extract_odds(self, match_url: str) -> Optional[Dict]:
        """Extract correct score odds for a specific match - REAL DATA ONLY"""
        print(f"🎯 Processing match: {match_url}")
        
        try:
            self.driver.get(match_url)
            time.sleep(5)
            
            self.debug_page(f"Match page: {match_url}")
            
            # Extract team names
            team_names = self.get_team_names(match_url)
            print(f"⚽ Teams: {team_names}")
            
            # Look for correct score section
            print("🔍 Looking for correct score markets...")
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Try to find correct score sections
            correct_score_keywords = [
                "correct score", "exact score", "final score", 
                "precise score", "score", "result"
            ]
            
            # Try clicking on expandable sections
            for keyword in correct_score_keywords:
                try:
                    elements = self.driver.find_elements(By.XPATH, 
                        f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
                    
                    if elements:
                        print(f"✅ Found '{keyword}' section")
                        try:
                            ActionChains(self.driver).move_to_element(elements[0]).click().perform()
                            time.sleep(3)
                            break
                        except:
                            pass
                except:
                    continue
            
            # Scroll to load more content
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract actual odds
            scores = {}
            score_pattern = r'\b\d+[-:]\d+\b'
            
            # Try multiple selectors for betting odds
            odds_selectors = [
                ".bet-button", ".coefficient", ".odds", ".outcome",
                "button", "*[class*='odd']", "*[class*='bet']",
                "*[title*='-']", "*[data-testid*='odd']"
            ]
            
            print("🎲 Searching for odds...")
            
            for selector in odds_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if self.debug and elements:
                        print(f"Selector '{selector}': found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            title = element.get_attribute('title') or ''
                            text = element.text.strip()
                            
                            # Look for score pattern
                            score_match = re.search(score_pattern, f"{title} {text}")
                            
                            if score_match:
                                score = score_match.group().replace(':', '-')
                                
                                # Look for odds value
                                odds_pattern = r'\b(\d+\.?\d*)\b'
                                odds_matches = re.findall(odds_pattern, text)
                                
                                for odds_text in odds_matches:
                                    try:
                                        odds_value = float(odds_text)
                                        if 1.1 <= odds_value <= 1000:  # Reasonable odds range
                                            scores[score] = odds_value
                                            print(f"💰 Found REAL odds: {score} -> {odds_value}")
                                            break
                                    except ValueError:
                                        continue
                        except:
                            continue
                
                except Exception as e:
                    if self.debug:
                        print(f"Error with selector '{selector}': {e}")
                    continue
                
                if len(scores) >= 5:  # Stop if we found enough
                    break
            
            if scores:
                print(f"✅ Successfully extracted {len(scores)} real odds")
                return {
                    "match": team_names,
                    "scores": scores
                }
            else:
                print("❌ No correct score odds found on this page")
                print("This could mean:")
                print("  - Match doesn't have correct score markets yet")
                print("  - Markets are not open")
                print("  - Different page structure")
                print("  - Site detected automation")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting odds: {e}")
            return None
    
    def scrape(self) -> List[Dict]:
        """Main scraping function - REAL DATA ONLY"""
        print("🏆 PARIMATCH PREMIER LEAGUE SCRAPER")
        print("=" * 50)
        print("⚠️ ONLY REAL DATA - NO FAKE ODDS!")
        print("=" * 50)
        
        results = []
        
        try:
            # Setup browser
            self.driver = self.setup_driver()
            
            # Find matches
            match_links = self.find_match_links()
            
            if not match_links:
                print("\n❌ NO REAL MATCH LINKS FOUND!")
                print("Cannot proceed without actual match URLs from Parimatch.")
                print("This means either:")
                print("  1. No Premier League matches are currently available")
                print("  2. The website structure has changed")
                print("  3. Site is blocking access")
                print("  4. Different URL/approach needed")
                return []
            
            print(f"\n📅 Processing {len(match_links)} real matches...")
            
            # Process each match
            for i, match_url in enumerate(match_links, 1):
                print(f"\n--- Match {i}/{len(match_links)} ---")
                
                try:
                    match_data = self.extract_odds(match_url)
                    if match_data:
                        results.append(match_data)
                        print(f"✅ Success: {match_data['match']}")
                    else:
                        print("⚠️ No odds data for this match")
                    
                    # Delay between requests
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    print(f"❌ Error processing match: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ Error in main scraper: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔒 Browser closed")


def main():
    """Main function for Google Colab"""
    print("🏆 PARIMATCH PREMIER LEAGUE SCRAPER - GOOGLE COLAB VERSION")
    print("=" * 60)
    print("This scraper extracts REAL odds from Parimatch - no fake data!")
    print("=" * 60)
    
    # Install dependencies first
    install_dependencies()
    setup_chrome_colab()
    
    # Initialize scraper with debug mode
    scraper = ParimatchScraper(debug=True)
    
    try:
        # Run the scraper
        results = scraper.scrape()
        
        if results:
            print(f"\n🎉 SUCCESS! Found REAL odds for {len(results)} matches")
            print("=" * 60)
            
            # Display results
            for i, match_data in enumerate(results, 1):
                print(f"\n{i}. {match_data['match']}")
                print("-" * len(f"{i}. {match_data['match']}"))
                
                for score, odds in match_data['scores'].items():
                    print(f"   {score:>5} : {odds:>6.1f}")
            
            # Output as JSON
            print(f"\n📋 JSON OUTPUT:")
            print(json.dumps(results, indent=2))
            
            # Save results
            with open('parimatch_real_odds.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to 'parimatch_real_odds.json'")
            
            return results
        else:
            print("\n❌ NO REAL ODDS FOUND!")
            print("This could mean:")
            print("- No Premier League matches are currently available for betting")
            print("- Markets are closed")
            print("- Website is blocking automated access") 
            print("- Site structure has changed")
            print("- Need different URL or approach")
            return []
            
    except KeyboardInterrupt:
        print("\n⚠️ Scraper stopped by user")
        return []
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return []

# For Google Colab usage
if __name__ == "__main__":
    main()

# GOOGLE COLAB INSTRUCTIONS:
"""
To run this in Google Colab:

1. Create a new notebook
2. First cell - Installation:
   !pip install selenium webdriver-manager
   !apt-get update
   !apt-get install -y chromium-browser chromium-chromedriver

3. Second cell - Copy this entire script and run it!

The script will:
- Setup Chrome browser automatically
- Scrape REAL odds from Parimatch
- Display results in your requested JSON format
- NO fake data - only real Premier League odds!
"""