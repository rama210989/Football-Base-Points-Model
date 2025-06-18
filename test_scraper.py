from fbref_scraper import fetch_team_player_stats

# Example: Man City 2023–24 team stats page
team_url = "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"
df = fetch_team_player_stats(team_url)

# Print key info
print("Columns:", df.columns.tolist())
print(df[['Player', 'Pos', 'Min']].head())
