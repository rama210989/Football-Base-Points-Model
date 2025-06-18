# fbref_scraper.py

import requests
import pandas as pd
from bs4 import BeautifulSoup


def fetch_team_player_stats(team_url):
    """
    Fetch all player stat tables from a FBref team page (e.g., Standard, Shooting, Passing, Defense).
    Args:
        team_url (str): Full URL of a FBref team season page.
    Returns:
        pandas.DataFrame: Combined DataFrame with all player stats merged.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    resp = requests.get(team_url, headers=headers)
    resp.raise_for_status()
    html = resp.text

    # FBref hides tables inside HTML comments
    soup = BeautifulSoup(html, 'html.parser')
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    dfs = []
    for c in comments:
        if "table" in c:
            try:
                table_soup = BeautifulSoup(c, 'html.parser')
                for table in table_soup.find_all("table"):
                    tbl_id = table.get("id", "")
                    if tbl_id.startswith("stats_"):
                        df = pd.read_html(str(table))[0]
                        df["source_tab"] = tbl_id
                        dfs.append(df)
            except Exception:
                continue

    if not dfs:
        raise ValueError("No stats tables found.")

    # Merge all tables on player name
    merged = dfs[0]
    for df in dfs[1:]:
        common_keys = list(set(df.columns) & set(merged.columns))
        if "Player" in common_keys:
            merged = pd.merge(merged, df, on=common_keys, suffixes=('', '_dup'), how='outer')

    return merged
