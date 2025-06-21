import os
import requests

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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://fbref.com/',
    'Connection': 'keep-alive',
}


output_folder = "html"
os.makedirs(output_folder, exist_ok=True)

for team, url in team_urls.items():
    print(f"Downloading {team} page...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        filename = f"{output_folder}/{team.replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Error downloading {team}: {e}")

print("Download complete!")

