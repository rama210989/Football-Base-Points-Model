import requests
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

SPREADEX_FIXTURES_URL = "https://www.spreadex.com/sports/model/api/SubscribeModel?modelRef=m1.s.d.coupon.panel:10047"

PREMIER_LEAGUE_TEAMS = {
    "Arsenal", "Liverpool", "Manchester City", "Chelsea", "Newcastle United",
    "Manchester United", "Tottenham", "Brighton", "Aston Villa", "West Ham United",
    "Crystal Palace", "Fulham", "Brentford", "Wolverhampton", "Everton",
    "Bournemouth", "Nottingham Forest", "Burnley", "Leeds United", "Sunderland"
}

TEAM_ALIASES = {
    "Man City": "Manchester City",
    "Man Utd": "Manchester United",
    "Spurs": "Tottenham",
    "Wolves": "Wolverhampton",
    "Nott'm Forest": "Nottingham Forest",
    "Sheff Utd": "Sheffield United",
    "West Ham": "West Ham United",
    "Brighton & Hove Albion": "Brighton",
    "Bournemouth": "Bournemouth",
    "Luton": "Luton Town",
    "Newcastle": "Newcastle United",
    "Aston Villa": "Aston Villa",
    "Crystal Palace": "Crystal Palace",
    "Brentford": "Brentford",
    "Fulham": "Fulham",
    "Burnley": "Burnley",
    "Everton": "Everton",
    "Chelsea": "Chelsea",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpool",
    "Leeds": "Leeds United",
    "Sunderland": "Sunderland"
}

def clean_team_name(name):
    name = name.strip()
    if name in PREMIER_LEAGUE_TEAMS:
        return name
    if name in TEAM_ALIASES:
        return TEAM_ALIASES[name]
    for team in PREMIER_LEAGUE_TEAMS:
        if name.lower() == team.lower():
            return team
    return None

def fetch_spreadex_fixtures():
    try:
        resp = requests.get(SPREADEX_FIXTURES_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # The structure is nested, so we need to find the matches
        matches = []
        # Look for 'markets' or 'events' in the JSON
        for key in data.get('model', {}):
            if 'markets' in data['model'][key]:
                for market in data['model'][key]['markets']:
                    # Each market may have 'eventName' or similar
                    event = market.get('eventName')
                    if event:
                        # Try to split event into teams
                        if ' v ' in event:
                            home, away = event.split(' v ', 1)
                        elif ' vs ' in event:
                            home, away = event.split(' vs ', 1)
                        else:
                            continue
                        home = clean_team_name(home)
                        away = clean_team_name(away)
                        if home and away and home != away:
                            matches.append(f"{home} vs {away}")
        if matches:
            logging.info(f"✅ Found {len(matches)} Premier League fixtures from Spreadex API:")
            for m in matches:
                print(m)
        else:
            logging.warning("❌ No valid Premier League fixtures found in Spreadex API response.")
    except Exception as e:
        logging.error(f"Failed to fetch or parse Spreadex fixtures: {e}")

if __name__ == "__main__":
    fetch_spreadex_fixtures()