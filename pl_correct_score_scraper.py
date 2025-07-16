import time
import re
import sys
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

# Premier League teams for 2023/24
PREMIER_LEAGUE_TEAMS = {
    "Arsenal", "Liverpool", "Manchester City", "Chelsea", "Newcastle United",
    "Manchester United", "Tottenham", "Brighton", "Aston Villa", "West Ham United",
    "Crystal Palace", "Fulham", "Brentford", "Wolverhampton", "Everton",
    "Bournemouth", "Nottingham Forest", "Burnley", "Sheffield United", "Luton Town"
}

# Team name aliases for cleaning
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
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Chrome driver setup for Colab
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')
CHROME_OPTIONS.add_argument('--no-sandbox')
CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')
CHROME_OPTIONS.add_argument('--disable-gpu')
CHROME_OPTIONS.add_argument('--window-size=1920,1080')
CHROME_OPTIONS.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
CHROME_OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])
CHROME_OPTIONS.add_experimental_option('useAutomationExtension', False)

# --- Utility Functions ---
def clean_team_name(name):
    name = name.strip()
    if name in PREMIER_LEAGUE_TEAMS:
        return name
    if name in TEAM_ALIASES:
        return TEAM_ALIASES[name]
    # Try to match ignoring case and whitespace
    for team in PREMIER_LEAGUE_TEAMS:
        if name.lower() == team.lower():
            return team
    return None

def extract_teams_from_text(text):
    # Remove times, dates, scores, extra whitespace
    text = re.sub(r'\d{1,2}:\d{2}', '', text)  # Remove times
    text = re.sub(r'\(.*?\)', '', text)  # Remove bracketed info
    text = re.sub(r'\bFT\b|\bKO\b|\bBST\b|\bGMT\b', '', text, flags=re.I)
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '-')  # Em dash
    text = text.replace('\u00a0', ' ')
    text = text.strip()
    # Try common separators
    for sep in [' vs ', ' v ', ' vs. ', ' - ', '–', '-', '—']:
        if sep in text:
            parts = text.split(sep)
            if len(parts) == 2:
                home = clean_team_name(parts[0])
                away = clean_team_name(parts[1])
                if home and away and home != away:
                    return [home, away]
    return None

def create_match_slug(home_team, away_team):
    # For Oddschecker: 'arsenal-v-liverpool'
    return f"{home_team.lower().replace(' ', '-')}-v-{away_team.lower().replace(' ', '-')}"

# --- Scraping Functions ---
def get_fixtures_bbc(driver):
    url = 'https://www.bbc.com/sport/football/premier-league/fixtures'
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fixtures = set()
    # BBC Sport: look for fixtures in the new structure
    for section in soup.find_all('section', {'class': 'qa-match-block'}):
        for match in section.find_all('div', {'class': 'sp-c-fixture'}):
            teams = match.find_all('span', {'class': 'sp-c-fixture__team-name'})
            if len(teams) == 2:
                home = clean_team_name(teams[0].get_text())
                away = clean_team_name(teams[1].get_text())
                if home and away and home != away:
                    fixtures.add((home, away))
    if not fixtures:
        logging.debug('BBC HTML snippet: ' + soup.prettify()[:2000])
    return list(fixtures)

def get_fixtures_espn(driver):
    url = 'https://www.espn.com/soccer/fixtures/_/league/eng.1'
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fixtures = set()
    # ESPN: look for team names in the new structure
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) >= 2:
                home = clean_team_name(tds[0].get_text())
                away = clean_team_name(tds[1].get_text())
                if home and away and home != away:
                    fixtures.add((home, away))
    if not fixtures:
        logging.debug('ESPN HTML snippet: ' + soup.prettify()[:2000])
    return list(fixtures)

def get_fixtures_skysports(driver):
    url = 'https://www.skysports.com/premier-league-fixtures'
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fixtures = set()
    # Sky Sports: look for fixtures in the new structure
    for match in soup.find_all('span', class_='matches__item-col--team-name'):
        # Each match is two consecutive spans
        home = clean_team_name(match.get_text())
        away_span = match.find_next_sibling('span', class_='matches__item-col--team-name')
        if away_span:
            away = clean_team_name(away_span.get_text())
            if home and away and home != away:
                fixtures.add((home, away))
    if not fixtures:
        logging.debug('SkySports HTML snippet: ' + soup.prettify()[:2000])
    return list(fixtures)

def get_fixtures_premierleague(driver):
    url = 'https://www.premierleague.com/fixtures'
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fixtures = set()
    # Premier League: look for fixtures in the JS-rendered structure
    for match in soup.find_all('div', class_='fixtures__matches-list'):
        for fixture in match.find_all('li', class_='matchFixtureContainer'):
            teams = fixture.find_all('span', class_='fixtures__team-name')
            if len(teams) == 2:
                home = clean_team_name(teams[0].get_text())
                away = clean_team_name(teams[1].get_text())
                if home and away and home != away:
                    fixtures.add((home, away))
    if not fixtures:
        logging.debug('PL HTML snippet: ' + soup.prettify()[:2000])
    return list(fixtures)

def get_real_fixtures(driver):
    for source, func in [
        ("BBC Sport", get_fixtures_bbc),
        ("ESPN", get_fixtures_espn),
        ("Sky Sports", get_fixtures_skysports),
        ("Premier League", get_fixtures_premierleague)
    ]:
        try:
            fixtures = func(driver)
            real_fixtures = [f for f in fixtures if f[0] in PREMIER_LEAGUE_TEAMS and f[1] in PREMIER_LEAGUE_TEAMS]
            if real_fixtures:
                logging.info(f"✅ Found {len(real_fixtures)} real fixtures from {source}")
                return real_fixtures
            else:
                logging.warning(f"❌ No valid fixtures found from {source}")
        except Exception as e:
            logging.warning(f"❌ Failed to scrape {source}: {e}")
    return []

def scrape_odds_oddschecker(driver, home_team, away_team):
    slug = create_match_slug(home_team, away_team)
    url = f"https://www.oddschecker.com/football/english/premier-league/{slug}/correct-score"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        odds = {}
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                score = cells[0].get_text(strip=True)
                odd = cells[1].get_text(strip=True)
                if re.match(r'\d+-\d+', score) and re.match(r'\d+\.\d+', odd):
                    odds[score] = float(odd)
        if odds:
            return odds
    except Exception as e:
        logging.warning(f"Oddschecker error for {home_team} vs {away_team}: {e}")
    return {}

def scrape_odds_oddsportal(driver, home_team, away_team):
    # OddsPortal main page, not per-match
    url = "https://www.oddsportal.com/football/england/premier-league/"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # OddsPortal is heavily JS, so this is best-effort
        odds = {}
        for row in soup.find_all('tr'):
            text = row.get_text()
            if home_team in text and away_team in text:
                for cell in row.find_all('td'):
                    m = re.match(r'(\d+-\d+)', cell.get_text())
                    if m:
                        score = m.group(1)
                        odd = cell.find_next('td').get_text()
                        if re.match(r'\d+\.\d+', odd):
                            odds[score] = float(odd)
        if odds:
            return odds
    except Exception as e:
        logging.warning(f"OddsPortal error for {home_team} vs {away_team}: {e}")
    return {}

def scrape_odds_skybet(driver, home_team, away_team):
    # SkyBet does not have a simple URL pattern, so we try the main page
    url = "https://www.skybet.com/football/premier-league"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        odds = {}
        for match in soup.find_all('div', string=re.compile(f"{home_team}.*{away_team}|{away_team}.*{home_team}", re.I)):
            for score in re.findall(r'(\d+-\d+)', match.get_text()):
                odd = re.search(rf'{score}\s+(\d+\.\d+)', match.get_text())
                if odd:
                    odds[score] = float(odd.group(1))
        if odds:
            return odds
    except Exception as e:
        logging.warning(f"SkyBet error for {home_team} vs {away_team}: {e}")
    return {}

def scrape_betting_odds(driver, home_team, away_team):
    for source, func in [
        ("Oddschecker", scrape_odds_oddschecker),
        ("OddsPortal", scrape_odds_oddsportal),
        ("SkyBet", scrape_odds_skybet)
    ]:
        try:
            odds = func(driver, home_team, away_team)
            if odds:
                logging.info(f"✅ {home_team} vs {away_team}: {len(odds)} real odds scraped from {source}")
                return odds
            else:
                logging.warning(f"❌ {home_team} vs {away_team}: No odds found from {source}")
        except Exception as e:
            logging.warning(f"❌ {home_team} vs {away_team}: {source} error: {e}")
        time.sleep(2)
    logging.warning(f"❌ {home_team} vs {away_team}: No real odds found - SKIPPED")
    return {}

# --- Main Script ---
def main():
    try:
        driver = webdriver.Chrome(options=CHROME_OPTIONS)
    except WebDriverException as e:
        logging.error(f"Could not start ChromeDriver: {e}")
        sys.exit(1)
    try:
        fixtures = get_real_fixtures(driver)
        if not fixtures:
            logging.error("❌ No real fixtures could be extracted from any source. All betting sites may be blocking access. 🚫 NO fake data generated - script only works with real data")
            return
        output_lines = []
        total_odds = 0
        for home, away in fixtures:
            odds = scrape_betting_odds(driver, home, away)
            if odds:
                for score, odd in odds.items():
                    output_lines.append(f"{home} vs {away} {score} {odd}")
                    total_odds += 1
            else:
                logging.warning(f"❌ {home} vs {away}: No real odds found - SKIPPED")
            time.sleep(2)
        if output_lines:
            with open('pl_correct_score_odds.txt', 'w') as f:
                for line in output_lines:
                    f.write(line + '\n')
            logging.info(f"✅ SUCCESS - {total_odds} real odds lines generated. Output saved to pl_correct_score_odds.txt")
        else:
            logging.error("❌ No real odds could be extracted from any fixtures. All betting sites may be blocking access. 🚫 NO fake data generated - script only works with real data")
    finally:
        driver.quit()

if __name__ == '__main__':
    main()