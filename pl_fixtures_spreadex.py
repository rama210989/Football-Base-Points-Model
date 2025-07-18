import requests
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

SPREADEX_FIXTURES_URL = "https://www.spreadex.com/sports/model/api/SubscribeModel?modelRef=m1.s.d.coupon.panel:10047"
ODDS_URL_TEMPLATE = "https://www.spreadex.com/sports/model/api/SubscribeModel?modelRef=m1.s.d.pricing-page.fo.group-panels:{}"

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
        matches = []
        panel_items = data.get('model', {}).get('panelItems', [])
        for item in panel_items:
            event = item.get('name')
            pricing_id = item.get('pricingPageId')
            if event and pricing_id:
                if ' v ' in event:
                    home, away = event.split(' v ', 1)
                elif ' vs ' in event:
                    home, away = event.split(' vs ', 1)
                else:
                    continue
                home = clean_team_name(home)
                away = clean_team_name(away)
                if home and away and home != away:
                    matches.append({
                        'home': home,
                        'away': away,
                        'pricingPageId': pricing_id
                    })
        if matches:
            logging.info(f"✅ Found {len(matches)} Premier League fixtures from Spreadex API.")
            return matches
        else:
            logging.warning("❌ No valid Premier League fixtures found in Spreadex API response.")
            return []
    except Exception as e:
        logging.error(f"Failed to fetch or parse Spreadex fixtures: {e}")
        return []

def fetch_correct_score_odds(pricing_page_id, home_team, away_team):
    odds_url = ODDS_URL_TEMPLATE.format(pricing_page_id)
    try:
        resp = requests.get(odds_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        panels = data.get('model', {}).get('panels', [])
        for panel in panels:
            for item in panel.get('panelItems', []):
                market = item.get('market', {})
                if market.get('marketName') == "Correct Score":
                    selections = panel.get('selectionsContainer', {}).get('panelSelections', [])
                    odds_lines = []
                    for sel in selections:
                        sel_data = sel.get('selection', {})
                        name = sel_data.get('name')
                        numerator = sel_data.get('numerator')
                        denominator = sel_data.get('denominator')
                        if name and numerator is not None and denominator:
                            # Extract just the score part (e.g., "2-1 Aston Villa" -> "2-1")
                            score = name.split(' ')[0]
                            decimal_odds = numerator / denominator + 1
                            odds_lines.append(f"{home_team} vs {away_team} {score} {decimal_odds:.2f}")
                    return odds_lines
        return []
    except Exception as e:
        logging.warning(f"Failed to fetch odds for {home_team} vs {away_team}: {e}")
        return []

def main():
    fixtures = fetch_spreadex_fixtures()
    if not fixtures:
        logging.error("❌ No real fixtures could be extracted from Spreadex. Script only works with real data.")
        return
    output_lines = []
    total_odds = 0
    for match in fixtures:
        home = match['home']
        away = match['away']
        pricing_id = match['pricingPageId']
        odds_lines = fetch_correct_score_odds(pricing_id, home, away)
        if odds_lines:
            output_lines.extend(odds_lines)
            total_odds += len(odds_lines)
            logging.info(f"✅ {home} vs {away}: {len(odds_lines)} correct score odds scraped.")
        else:
            logging.warning(f"❌ {home} vs {away}: No correct score odds found - SKIPPED")
        time.sleep(1)  # Be polite to the server
    if output_lines:
        with open('pl_correct_score_odds.txt', 'w') as f:
            for line in output_lines:
                f.write(line + '\n')
        logging.info(f"✅ SUCCESS - {total_odds} real odds lines generated. Output saved to pl_correct_score_odds.txt")
    else:
        logging.error("❌ No real odds could be extracted from any fixtures. Script only works with real data.")

if __name__ == "__main__":
    main()