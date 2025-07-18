import requests
from bs4 import BeautifulSoup
import logging
import sys
import time
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

FIXTURES_URL = "https://www.flashscore.in/football/england/premier-league/fixtures/"
ODDS_URL_TEMPLATE = "https://global.ds.lsapp.eu/odds/pq_graphql?_hash=oce&eventId={}&projectId=26&geoIpCode=IN&geoIpSubdivisionCode=INTN"
HEADERS = {"User-Agent": "Mozilla/5.0"}

TEAM_CLEANUP = {
    # Add more mappings if needed for consistency
    "Man City": "Manchester City",
    "Man Utd": "Manchester United",
    "Spurs": "Tottenham",
    "Wolves": "Wolverhampton",
    "Nott'm Forest": "Nottingham Forest",
    "Sheff Utd": "Sheffield United",
    "West Ham": "West Ham United",
    "Brighton & Hove Albion": "Brighton",
    "Luton": "Luton Town",
}

PREMIER_LEAGUE_TEAMS = {
    "Arsenal", "Liverpool", "Manchester City", "Chelsea", "Newcastle United",
    "Manchester United", "Tottenham", "Brighton", "Aston Villa", "West Ham United",
    "Crystal Palace", "Fulham", "Brentford", "Wolverhampton", "Everton",
    "Bournemouth", "Nottingham Forest", "Burnley", "Leeds United", "Sunderland"
}

def clean_team_name(name):
    name = name.strip()
    if name in PREMIER_LEAGUE_TEAMS:
        return name
    if name in TEAM_CLEANUP:
        return TEAM_CLEANUP[name]
    for team in PREMIER_LEAGUE_TEAMS:
        if name.lower() == team.lower():
            return team
    return name

def fetch_fixtures():
    try:
        resp = requests.get(FIXTURES_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        fixtures = []
        # Find all match links
        for a in soup.find_all('a', href=True):
            m = re.match(r"/match/([a-zA-Z0-9]+)/#", a['href'])
            if m:
                event_id = m.group(1)
                # Try to get team names from the link text or nearby elements
                text = a.get_text(separator=" ", strip=True)
                if ' - ' in text:
                    home, away = text.split(' - ', 1)
                else:
                    # Try to find team names in parent or sibling elements
                    parent = a.find_parent()
                    if parent:
                        teams = parent.get_text(separator=" ", strip=True)
                        if ' - ' in teams:
                            home, away = teams.split(' - ', 1)
                        else:
                            continue
                    else:
                        continue
                home = clean_team_name(home)
                away = clean_team_name(away)
                if home and away and home != away:
                    fixtures.append({
                        'event_id': event_id,
                        'home': home,
                        'away': away
                    })
        # Remove duplicates (some links may repeat)
        seen = set()
        unique_fixtures = []
        for f in fixtures:
            key = (f['event_id'], f['home'], f['away'])
            if key not in seen:
                unique_fixtures.append(f)
                seen.add(key)
        logging.info(f"Found {len(unique_fixtures)} fixtures with event IDs.")
        return unique_fixtures
    except Exception as e:
        logging.error(f"Failed to fetch or parse fixtures: {e}")
        return []

def fetch_correct_score_odds(event_id):
    url = ODDS_URL_TEMPLATE.format(event_id)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
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
                        odds_lines.append(f"{score}: {value}")
                return odds_lines
        return []
    except Exception as e:
        logging.warning(f"Failed to fetch odds for event ID {event_id}: {e}")
        return []

def main():
    fixtures = fetch_fixtures()
    for f in fixtures:
        home = f['home']
        away = f['away']
        event_id = f['event_id']
        print(f"\n{home} vs {away} (Event ID: {event_id})")
        odds = fetch_correct_score_odds(event_id)
        if odds:
            for line in odds:
                print(line)
        else:
            print("No correct score odds found or market not available.")
        time.sleep(1)  # Be polite to the server

if __name__ == "__main__":
    main()