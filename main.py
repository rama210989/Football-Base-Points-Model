import asyncio
from playwright.async_api import async_playwright
import requests
import csv
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

ODDS_URL_TEMPLATE = "https://global.ds.lsapp.eu/odds/pq_graphql?_hash=oce&eventId={}&projectId=26&geoIpCode=IN&geoIpSubdivisionCode=INTN"
FIXTURES_URL = "https://www.flashscore.in/football/england/premier-league/fixtures/"
CSV_FILE = "premier_league_fixtures_and_odds.csv"

async def get_fixtures():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        logging.info(f"Navigating to {FIXTURES_URL}")
        await page.goto(FIXTURES_URL, timeout=60000)
        # Dump the loaded HTML for debugging
        html = await page.content()
        with open("debug_flashscore.html", "w", encoding="utf-8") as f:
            f.write(html)
        logging.info("Saved loaded HTML to debug_flashscore.html")
        print(html[:2000])  # Print the first 2000 characters to the logs
        # Optionally, wait a bit for JS to load
        await page.wait_for_timeout(5000)
        try:
            await page.wait_for_selector('a[href^="/match/"]', timeout=10000)
        except Exception as e:
            logging.error(f"Selector for match links not found: {e}")
            return []
        links = await page.query_selector_all('a[href^="/match/"]')
        fixtures = []
        seen = set()
        for a in links:
            href = await a.get_attribute('href')
            text = await a.inner_text()
            if not href or not text or ' - ' not in text:
                continue
            event_id = href.split('/')[2]
            home, away = text.split(' - ', 1)
            key = (event_id, home.strip(), away.strip())
            if key in seen:
                continue
            seen.add(key)
            fixtures.append({'event_id': event_id, 'home': home.strip(), 'away': away.strip()})
        await browser.close()
        logging.info(f"Found {len(fixtures)} fixtures with event IDs.")
        if not fixtures:
            logging.warning("No fixtures found. Check debug_flashscore.html for clues (Cloudflare, empty, etc.)")
        return fixtures

def fetch_correct_score_odds(event_id):
    url = ODDS_URL_TEMPLATE.format(event_id)
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        odds_data = data.get('data', {}).get('eventOdds', [])
        for market in odds_data:
            if market.get('bettingType') == 'CORRECT_SCORE' and market.get('bettingScope') == 'FULL_TIME':
                odds = market.get('odds', [])
                odds_lines = []
                for item in odds:
                    score = item.get('score')
                    value = item.get('value')
                    if score and value:
                        odds_lines.append({'score': score, 'odds': value})
                return odds_lines
        return []
    except Exception as e:
        logging.warning(f"Failed to fetch odds for event ID {event_id}: {e}")
        return []

def main():
    fixtures = asyncio.run(get_fixtures())
    all_rows = []
    for f in fixtures:
        home = f['home']
        away = f['away']
        event_id = f['event_id']
        print(f"\n{home} vs {away} (Event ID: {event_id})")
        odds = fetch_correct_score_odds(event_id)
        if odds:
            for line in odds:
                print(f"  {line['score']}: {line['odds']}")
                all_rows.append({
                    'home': home,
                    'away': away,
                    'event_id': event_id,
                    'score': line['score'],
                    'odds': line['odds']
                })
        else:
            print("  No correct score odds found or market not available.")
        time.sleep(1)  # Be polite to the server
    # Write to CSV
    if all_rows:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['home', 'away', 'event_id', 'score', 'odds'])
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nResults saved to {CSV_FILE}")
    else:
        print("\nNo odds data to save.")

if __name__ == "__main__":
    main()