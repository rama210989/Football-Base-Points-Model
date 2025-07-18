import requests
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# User: Fill this mapping with event IDs from Flashscore for each fixture
# Example: {"Liverpool vs Bournemouth": "jqWq8sIi", ...}
FIXTURE_TO_EVENT_ID = {
    # "Liverpool vs Bournemouth": "jqWq8sIi",
    # ...
}

FLASHCORE_ODDS_URL_TEMPLATE = "https://global.ds.lsapp.eu/odds/pq_graphql?_hash=oce&eventId={}&projectId=26&geoIpCode=IN&geoIpSubdivisionCode=INTN"

# List of fixtures to fetch odds for (from your Spreadex script)
FIXTURES = [
    "Liverpool vs Bournemouth",
    "Aston Villa vs Newcastle United",
    "Brighton vs Fulham",
    "Sunderland vs West Ham United",
    "Tottenham vs Burnley",
    "Wolverhampton vs Manchester City",
    "Chelsea vs Crystal Palace",
    "Nottingham Forest vs Brentford",
    "Manchester United vs Arsenal",
    "Leeds United vs Everton"
]

def fetch_flashscore_correct_score_odds(event_id):
    url = FLASHCORE_ODDS_URL_TEMPLATE.format(event_id)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Find correct score odds in the response
        odds_data = data.get('data', {}).get('eventOdds', [])
        for market in odds_data:
            if market.get('bettingType') == 'CORRECT_SCORE' and market.get('bettingScope') == 'FULL_TIME':
                odds = market.get('odds', [])
                odds_lines = []
                for item in odds:
                    score = item.get('score')
                    value = item.get('value')
                    if score and value:
                        odds_lines.append(f"{score}: {value}")
                return odds_lines
        return []
    except Exception as e:
        logging.warning(f"Failed to fetch odds for event ID {event_id}: {e}")
        return []

def main():
    for fixture in FIXTURES:
        event_id = FIXTURE_TO_EVENT_ID.get(fixture)
        if not event_id:
            logging.warning(f"No Flashscore event ID mapped for fixture: {fixture}")
            continue
        odds = fetch_flashscore_correct_score_odds(event_id)
        print(f"\nCorrect Score Odds for {fixture} (Event ID: {event_id}):")
        if odds:
            for line in odds:
                print(line)
        else:
            print("No odds found or market not available.")
        time.sleep(1)  # Be polite to the server

if __name__ == "__main__":
    main()