import asyncio
from playwright.async_api import async_playwright
import csv
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

FIXTURES_URL = "https://www.spreadex.com/sports/en-GB/spread-betting/football/league/47/fo/c66"
BASE_URL = "https://www.spreadex.com"
CSV_FILE = "spreadex_premier_league_correct_score_odds.csv"

async def get_fixture_links(page):
    await page.goto(FIXTURES_URL, timeout=60000)
    await page.wait_for_timeout(5000)  # Wait for JS to load
    # Find all fixture links (those that go to a match odds page)
    links = await page.query_selector_all('a[href*="/spread-betting/football/premier-league/"][href*="/fo/p"]')
    fixtures = []
    seen = set()
    for a in links:
        href = await a.get_attribute('href')
        text = await a.inner_text()
        if not href or not text:
            continue
        # Only keep unique fixtures
        if href in seen:
            continue
        seen.add(href)
        # Try to extract home and away from the URL or text
        # URL: .../premier-league/home-v-away/fo/pXXXXXXX
        parts = href.split('/')
        if len(parts) > 6 and '-v-' in parts[-3]:
            teams = parts[-3].split('-v-')
            home = teams[0].replace('-', ' ').title()
            away = teams[1].replace('-', ' ').title()
        else:
            # fallback: use text
            if ' v ' in text:
                home, away = text.split(' v ', 1)
            else:
                continue
        fixtures.append({'url': BASE_URL + href, 'home': home.strip(), 'away': away.strip()})
    logging.info(f"Found {len(fixtures)} fixture links.")
    return fixtures

async def get_correct_score_odds(page, fixture):
    url = fixture['url']
    home = fixture['home']
    away = fixture['away']
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)
        # Try to find the 'Correct Score' tab/button and click it if needed
        # This selector may need adjustment if Spreadex changes their UI
        tab = await page.query_selector('button:has-text("Correct Score")')
        if tab:
            await tab.click()
            await page.wait_for_timeout(2000)
        # Odds are usually in a table or list under the correct score section
        odds = []
        # Try to find all rows with score and odds
        rows = await page.query_selector_all('[data-testid*="correct-score"] [data-testid*="selection-row"]')
        if not rows:
            # fallback: try to find any table rows with score/odds
            rows = await page.query_selector_all('tr')
        for row in rows:
            # Try to extract score and odds from the row
            score = None
            odds_val = None
            # Try to get all text in the row
            cells = await row.query_selector_all('td, div')
            texts = [await c.inner_text() for c in cells]
            # Heuristic: look for a cell with a score pattern (e.g., 2-1, 1-0, etc.)
            for t in texts:
                if t and (':' in t or '-' in t) and any(char.isdigit() for char in t):
                    score = t.replace(':', '-').strip()
                    break
            # Heuristic: odds are usually a float or fraction, last cell
            for t in reversed(texts):
                if t and ('.' in t or '/' in t):
                    odds_val = t.strip()
                    break
            if score and odds_val:
                odds.append({'score': score, 'odds': odds_val})
        return odds
    except Exception as e:
        logging.warning(f"Failed to fetch odds for {home} vs {away}: {e}")
        return []

async def main_async():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        fixtures = await get_fixture_links(page)
        all_rows = []
        for fixture in fixtures:
            home = fixture['home']
            away = fixture['away']
            odds = await get_correct_score_odds(page, fixture)
            print(f"\n{home} vs {away}")
            if odds:
                for line in odds:
                    print(f"  {line['score']}: {line['odds']}")
                    all_rows.append({
                        'home': home,
                        'away': away,
                        'score': line['score'],
                        'odds': line['odds']
                    })
            else:
                print("  No correct score odds found or market not available.")
            time.sleep(1)  # Be polite to the server
        await browser.close()
        # Write to CSV
        if all_rows:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['home', 'away', 'score', 'odds'])
                writer.writeheader()
                writer.writerows(all_rows)
            print(f"\nResults saved to {CSV_FILE}")
        else:
            print("\nNo odds data to save.")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()