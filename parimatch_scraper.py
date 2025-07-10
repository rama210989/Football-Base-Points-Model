#!/usr/bin/env python3
"""
Parimatch Premier League Correct Score Odds Scraper

This script scrapes correct score odds for upcoming Premier League matches 
from Parimatch using Selenium with undetected-chromedriver to avoid detection.
"""

import json
import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains


class ParimatchScraper:
    def __init__(self, headless: bool = True):
        """Initialize the scraper with Chrome options."""
        self.base_url = "https://parimatchglobal.com"
        self.premier_league_url = "https://parimatchglobal.com/en/football/premier-league-7f5506e872d14928adf0613efa509494/prematch"
        self.driver = None
        self.headless = headless
        
    def setup_driver(self) -> uc.Chrome:
        """Setup and configure the Chrome driver with anti-detection measures."""
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        # Basic anti-detection options that are more compatible
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        # Set realistic window size
        options.add_argument("--window-size=1920,1080")
        
        # User agent to appear more like a real browser
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            driver = uc.Chrome(options=options, version_main=None)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            print(f"Failed to setup undetected Chrome driver: {e}")
            raise
    
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for the page to fully load."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            print(f"Page didn't load within {timeout} seconds")
            return False
    
    def extract_match_links(self) -> List[str]:
        """Extract links to individual match pages from the Premier League page."""
        print("Navigating to Premier League page...")
        
        try:
            self.driver.get(self.premier_league_url)
            self.wait_for_page_load()
            
            # Wait for match cards to load
            print("Waiting for match cards to load...")
            time.sleep(5)
            
            # Try multiple selectors for match links
            selectors = [
                "a[href*='/en/events/']",
                "a[href*='/events/']",
                ".event-card a",
                ".match-card a",
                "[data-testid*='event'] a",
                ".prematch-event a"
            ]
            
            match_links = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/events/' in href:
                            full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                            if full_url not in match_links:
                                match_links.append(full_url)
                    
                    if match_links:
                        break
                except NoSuchElementException:
                    continue
            
            # If no links found, try scrolling and looking again
            if not match_links:
                print("No match links found initially, trying to scroll...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Try again after scrolling
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            href = element.get_attribute('href')
                            if href and '/events/' in href:
                                full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                                if full_url not in match_links:
                                    match_links.append(full_url)
                        
                        if match_links:
                            break
                    except NoSuchElementException:
                        continue
            
            print(f"Found {len(match_links)} match links")
            return match_links
            
        except Exception as e:
            print(f"Error extracting match links: {e}")
            return []
    
    def extract_team_names(self, match_url: str) -> Optional[str]:
        """Extract team names from the match page."""
        try:
            # Try multiple selectors for team names
            team_selectors = [
                ".event-header .team-name",
                ".match-header .team",
                ".event-title h1",
                "h1",
                ".teams .team-name",
                "[data-testid*='team']"
            ]
            
            teams = []
            for selector in team_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 2:
                        teams = [elem.text.strip() for elem in elements[:2]]
                        break
                    elif len(elements) == 1:
                        # Sometimes team names are in a single element separated by "vs" or "-"
                        text = elements[0].text.strip()
                        if ' vs ' in text:
                            teams = text.split(' vs ')
                        elif ' - ' in text:
                            teams = text.split(' - ')
                        if len(teams) == 2:
                            break
                except:
                    continue
            
            if len(teams) == 2:
                return f"{teams[0].strip()} vs {teams[1].strip()}"
            
            # Fallback: try to extract from URL or page title
            try:
                title = self.driver.title
                if 'vs' in title.lower():
                    return title.split('|')[0].strip()
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error extracting team names: {e}")
            return None
    
    def extract_correct_score_odds(self, match_url: str) -> Optional[Dict]:
        """Extract correct score odds for a specific match."""
        print(f"Processing match: {match_url}")
        
        try:
            self.driver.get(match_url)
            self.wait_for_page_load()
            time.sleep(3)
            
            # Extract team names
            team_names = self.extract_team_names(match_url)
            if not team_names:
                print("Could not extract team names")
                return None
            
            print(f"Teams: {team_names}")
            
            # Look for correct score section
            correct_score_selectors = [
                "*[title*='Correct Score' i]",
                "*[data-title*='correct score' i]",
                "*:contains('Correct Score')",
                ".correct-score",
                "*[aria-label*='correct score' i]"
            ]
            
            correct_score_section = None
            
            # Try to find and click on correct score section
            for selector in correct_score_selectors:
                try:
                    if selector.startswith("*:contains"):
                        # Use XPath for text content search
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'correct score')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        correct_score_section = elements[0]
                        print("Found correct score section")
                        # Try to click to expand
                        try:
                            ActionChains(self.driver).move_to_element(correct_score_section).click().perform()
                            time.sleep(2)
                        except:
                            pass
                        break
                except:
                    continue
            
            # If no specific section found, scroll down to look for odds
            if not correct_score_section:
                print("Correct score section not found, scrolling to look for odds...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract score odds
            scores = {}
            
            # Look for score patterns and odds
            score_patterns = [
                r'\b\d+[-:]\d+\b',  # Matches "1-0", "2:1", etc.
            ]
            
            # Try multiple selectors for odds elements
            odds_selectors = [
                ".bet-button",
                ".coefficient",
                ".odds",
                "[data-testid*='odd']",
                ".outcome",
                "button[title*='-']",
                "*[title*='-']"
            ]
            
            for selector in odds_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        try:
                            # Check title attribute for score
                            title = element.get_attribute('title') or ''
                            text = element.text.strip()
                            
                            score_match = None
                            odds_value = None
                            
                            # Look for score pattern in title or text
                            for pattern in score_patterns:
                                if re.search(pattern, title):
                                    score_match = re.search(pattern, title).group()
                                    break
                                elif re.search(pattern, text):
                                    score_match = re.search(pattern, text).group()
                                    break
                            
                            if score_match:
                                # Try to find odds value
                                odds_text = text.replace(score_match, '').strip()
                                
                                # Look for decimal odds
                                odds_pattern = r'\b\d+\.?\d*\b'
                                odds_matches = re.findall(odds_pattern, odds_text)
                                
                                if odds_matches:
                                    try:
                                        odds_value = float(odds_matches[-1])  # Take the last number found
                                        if odds_value > 1:  # Sanity check for odds
                                            score_match = score_match.replace(':', '-')  # Normalize separator
                                            scores[score_match] = odds_value
                                            print(f"Found: {score_match} -> {odds_value}")
                                    except ValueError:
                                        continue
                        except:
                            continue
                            
                    if scores:
                        break
                except:
                    continue
            
            if scores:
                return {
                    "match": team_names,
                    "scores": scores
                }
            else:
                print("No correct score odds found")
                return None
                
        except Exception as e:
            print(f"Error extracting odds for {match_url}: {e}")
            return None
    
    def scrape_all_matches(self) -> List[Dict]:
        """Scrape correct score odds for all Premier League matches."""
        results = []
        
        try:
            self.driver = self.setup_driver()
            
            # Extract match links
            match_links = self.extract_match_links()
            
            if not match_links:
                print("No match links found!")
                return results
            
            print(f"Processing {len(match_links)} matches...")
            
            # Process each match
            for i, match_url in enumerate(match_links, 1):
                print(f"\n--- Processing match {i}/{len(match_links)} ---")
                
                try:
                    match_data = self.extract_correct_score_odds(match_url)
                    if match_data:
                        results.append(match_data)
                        print(f"Successfully extracted data for: {match_data['match']}")
                    else:
                        print("No data extracted for this match")
                    
                    # Small delay between matches
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error processing match {match_url}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error in scrape_all_matches: {e}")
            return results
        
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main function to run the scraper."""
    print("Starting Parimatch Premier League Correct Score Scraper...")
    
    # Initialize scraper (set headless=False for debugging)
    scraper = ParimatchScraper(headless=True)
    
    try:
        # Scrape all matches
        results = scraper.scrape_all_matches()
        
        if results:
            print(f"\n{'='*50}")
            print(f"SCRAPING COMPLETED - Found {len(results)} matches with odds")
            print(f"{'='*50}")
            
            # Print results
            for match_data in results:
                print(f"\nMatch: {match_data['match']}")
                print("Correct Score Odds:")
                for score, odds in match_data['scores'].items():
                    print(f"  {score}: {odds}")
            
            # Save to JSON file
            with open('parimatch_odds.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nResults saved to 'parimatch_odds.json'")
            
            return results
        else:
            print("No odds data found!")
            return []
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


if __name__ == "__main__":
    main()