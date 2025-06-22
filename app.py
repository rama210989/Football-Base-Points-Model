import streamlit as st
import pandas as pd
import requests
import time

# Updated FBref URLs (double-check team IDs)
team_urls = {
    "Arsenal": "https://fbref.com/en/squads/18bb7c10/2024-2025/Arsenal-Stats",
    "Aston Villa": "https://fbref.com/en/squads/8602292d/2024-2025/Aston-Villa-Stats",
    "Bournemouth": "https://fbref.com/en/squads/bffc15f4/2024-2025/Bournemouth-Stats",
    "Brentford": "https://fbref.com/en/squads/7c21e445/2024-2025/Brentford-Stats",
    "Brighton": "https://fbref.com/en/squads/bd87cffa/2024-2025/Brighton-and-Hove-Albion-Stats",
    "Chelsea": "https://fbref.com/en/squads/cff3d9bb/2024-2025/Chelsea-Stats",
    "Crystal Palace": "https://fbref.com/en/squads/47c64c55/2024-2025/Crystal-Palace-Stats",
    "Everton": "https://fbref.com/en/squads/d3fd31cc/2024-2025/Everton-Stats",
    "Fulham": "https://fbref.com/en/squads/fd962109/2024-2025/Fulham-Stats",
    "Leeds United": "https://fbref.com/en/squads/5bfb9651/2024-2025/Leeds-United-Stats",
    "Leicester City": "https://fbref.com/en/squads/6eb4d45d/2024-2025/Leicester-City-Stats",
    "Liverpool": "https://fbref.com/en/squads/822bd0ba/2024-2025/Liverpool-Stats",
    "Manchester City": "https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats",
    "Manchester United": "https://fbref.com/en/squads/19538871/2024-2025/Manchester-United-Stats",
    "Newcastle United": "https://fbref.com/en/squads/b2b47a98/2024-2025/Newcastle-United-Stats",
    "Nottingham Forest": "https://fbref.com/en/squads/1c781004/2024-2025/Nottingham-Forest-Stats",
    "Southampton": "https://fbref.com/en/squads/33c895d4/2024-2025/Southampton-Stats",
    "Tottenham Hotspur": "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats",
    "West Ham United": "https://fbref.com/en/squads/7c21e445/2024-2025/West-Ham-United-Stats",
    "Wolverhampton Wanderers": "https://fbref.com/en/squads/8cec06e1/2024-2025/Wolverhampton-Wanderers-Stats"
}

def safe_table(tables, idx):
    try:
        return tables[idx]
    except IndexError:
        return pd.DataFrame()

def load_team_data_from_url(url, team_name):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        tables = pd.read_html(res.text)
        time.sleep(2)  # be polite
    except Exception as e:
        st.error(f"Failed to load page for {team_name}: {e}")
        return None

    try:
        df_basic = safe_table(tables, 0)
        if df_basic.empty:
            raise Exception("Basic stats table not found")

        df_basic.columns = [' '.join(col).strip() for col in df_basic.columns.values]
        df_basic = df_basic[df_basic['Unnamed: 0_level_0 Player'] != 'Player']
        df_basic.rename(columns={
            'Unnamed: 0_level_0 Player': 'Player',
            'Unnamed: 2_level_0 Pos': 'Pos',
            'Playing Time Starts': 'Starts',
            'Performance CrdY': 'YC',
            'Performance CrdR': 'RC',
            'Performance OG': 'OG',
            'Unnamed: 4_level_0 MP': 'Matches'
        }, inplace=True, errors="ignore")

        def clean_df(tables, idx, column_renames):
            df = safe_table(tables, idx)
            if df.empty: return pd.DataFrame()
            df.columns = [' '.join(col).strip() for col in df.columns.values]
            df = df[df[df.columns[0]] != df.columns[0]]
            df.rename(columns=column_renames, inplace=True, errors="ignore")
            return df

        df_pass = clean_df(tables, 6, {'Unnamed: 0_level_0 Player': 'Player', 'Outcomes Cmp': 'Passes_Completed'})
        df_sca = clean_df(tables, 7, {'Unnamed: 0_level_0 Player': 'Player', 'SCA SCA': 'Chance_Created'})
        df_standard = clean_df(tables, 4, {'Unnamed: 0_level_0 Player': 'Player', 'Standard SoT': 'Shots_on_Target'})
        df_gk = clean_df(tables, 2, {'Unnamed: 0_level_0 Player': 'Player', 'Performance Saves': 'Saves', 'Performance GA': 'Goals_Against'})
        df_def_misc = clean_df(tables, 11, {'Unnamed: 0_level_0 Player': 'Player', 'Performance Int': 'Interceptions', 'Performance TklW': 'Tackles_Won'})

        df_all = df_basic
        for extra in [df_pass, df_sca, df_standard, df_def_misc, df_gk]:
            if not extra.empty:
                df_all = df_all.merge(extra[['Player'] + [col for col in extra.columns if col != 'Player']], on='Player', how='left')

        df_all.fillna(0, inplace=True)
        numeric_cols = ['Matches', 'Starts', 'YC', 'RC', 'OG', 'Passes_Completed', 'Chance_Created',
                        'Shots_on_Target', 'Tackles_Won', 'Interceptions', 'Saves', 'Goals_Against']
        for col in numeric_cols:
            df_all[col] = pd.to_numeric(df_all.get(col, 0), errors='coerce').fillna(0)

        df_all['Team'] = team_name
        return df_all

    except Exception as e:
        st.error(f"Failed to parse stats for {team_name}: {e}")
        return None

def calc_points(row):
    points = 0
    points += row.get('Chance_Created', 0) * 3
    points += row.get('Shots_on_Target', 0) * 6
    points += (row.get('Passes_Completed', 0) // 5) * 1
    points += row.get('Tackles_Won', 0) * 4
    points += row.get('Interceptions', 0) * 4
    points += row.get('Saves', 0) * 6
    points += (row.get('Starts', 0) > 0) * 4
    points += (row.get('Matches', 0) - row.get('Starts', 0)) * 2
    points -= row.get('YC', 0) * 4
    points -= row.get('RC', 0) * 10
    points -= row.get('OG', 0) * 8
    if row.get('Pos') in ['GK', 'DF']:
        points -= row.get('Goals_Against', 0) * 2
    return points

def select_best_11(df):
    df['Points'] = df.apply(calc_points, axis=1)
    df = df.sort_values(by='Points', ascending=False)

    selected = []
    count_team = {}
    pos_count = {'GK': 0, 'DF': 0, 'MF': 0, 'FW': 0}

    def pos_key(pos):
        pos = str(pos).upper()
        if 'GK' in pos: return 'GK'
        elif 'DF' in pos: return 'DF'
        elif 'MF' in pos: return 'MF'
        elif 'FW' in pos: return 'FW'
        else: return None

    for _, row in df.iterrows():
        if len(selected) == 11:
            break
        team = row['Team']
        pos = pos_key(row['Pos'])
        if not pos:
            continue
        if count_team.get(team, 0) >= 7:
            continue
        if pos_count[pos] >= {'GK': 1, 'DF': 5, 'MF': 5, 'FW': 3}[pos]:
            continue

        selected.append(row)
        count_team[team] = count_team.get(team, 0) + 1
        pos_count[pos] += 1

    return pd.DataFrame(selected)[['Player', 'Pos', 'Team', 'Points']]

# Streamlit UI
st.title("Premier League Dream11 Best Playing 11 Selector")

teams = list(team_urls.keys())
team1 = st.selectbox("Select Team 1", teams, key="t1")
team2 = st.selectbox("Select Team 2", teams, key="t2")

if st.button("Select Best Playing 11"):
    if team1 == team2:
        st.error("Please select two different teams.")
    else:
        with st.spinner("Fetching data and computing best 11..."):
            df1 = load_team_data_from_url(team_urls[team1], team1)
            df2 = load_team_data_from_url(team_urls[team2], team2)
            if df1 is not None and df2 is not None:
                best_11 = select_best_11(pd.concat([df1, df2], ignore_index=True))
                st.table(best_11)
            else:
                st.error("One or both teams failed to load.")
