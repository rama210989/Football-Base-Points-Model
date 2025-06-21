# download_teams_html.py

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Setup headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/local/bin/chrome/chrome"

service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

team_urls = {
    "Arsenal": "https://fbref.com/en/squads/18bb7c10/2024-2025/Arsenal-Stats",
    "Aston Villa": "https://fbref.com/en/squads/8602292d/2024-2025/Aston-Villa-Stats",
    "Bournemouth": "https://fbref.com/en/squads/bffc15f4/2024-2025/Bournemouth-Stats",
    "Brentford": "https://fbref.com/en/squads/7c21e445/2024-2025/Brentford-Stats",
    "Brighton": "https://fbref.com/en/squads/bd87cffa/2024-2025/Brighton-and-Hove-Albion-Stats",
    "Chelsea": "https://fbref.com/en/squads/cff3d9bb/2024-2025/Chelsea-Stats",
    "Crystal Palace": "https://fbref.com/en/squads/47c64c55/2024-2025/Crystal-Palace-Stats",
    "Everton": "https://fbref.com/en/squads/7c21e445/2024-2025/Everton-Stats",
    "Fulham": "https://fbref.com/en/squads/3fab645c/2024-2025/Fulham-Stats",
    "Leeds United": "https://fbref.com/en/squads/2a89072c/2024-2025/Leeds-United-Stats",
    "Leicester City": "https://fbref.com/en/squads/8656c477/2024-2025/Leicester-City-Stats",
    "Liverpool": "https://fbref.com/en/squads/822bd0ba/2024-2025/Liverpool-Stats",
    "Manchester City": "https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats",
    "Manchester United": "https://fbref.com/en/squads/19538871/2024-2025/Manchester-United-Stats",
    "Newcastle United": "https://fbref.com/en/squads/b2b47a98/2024-2025/Newcastle-United-Stats",
    "Nottingham Forest": "https://fbref.com/en/squads/1c781004/2024-2025/Nottingham-Forest-Stats",
    "Southampton": "https://fbref.com/en/squads/5c95d9f7/2024-2025/Southampton-Stats",
    "Tottenham Hotspur": "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats",
    "West Ham United": "https://fbref.com/en/squads/1a2dee49/2024-2025/West-Ham-United-Stats",
    "Wolverhampton Wanderers": "https://fbref.com/en/squads/19538871/2024-2025/Wolverhampton-Wanderers-Stats",
}

output_folder = "html"
os.makedirs(output_folder, exist_ok=True)

for team, url in team_urls.items():
    print(f"📥 Downloading {team} page...")
    driver.get(url)
    time.sleep(3)
    html = driver.page_source
    filename = f"{output_folder}/{team.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Saved {filename}")

driver.quit()
print("🎉 All team pages downloaded.")
