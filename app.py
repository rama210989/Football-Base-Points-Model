import streamlit as st
import pandas as pd
import requests

# Hardcoded Premier League teams with fbref URLs
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

def load_team_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html = response.text

    tables = pd.read_html(html)

    df_basic = tables[0]
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
    }, inplace=True)

    df_pass = tables[6]
    df_pass.columns = [' '.join(col).strip() for col in df_pass.columns.values]
    df_pass = df_pass[df_pass['Unnamed: 0_level_0 Player'] != 'Player']
    df_pass.rename(columns={
        'Unnamed: 0_level_0 Player': 'Player',
        'Outcomes Cmp': 'Passes_Completed'
    }, inplace=True)

    df_sca = tables[7]
    df_sca.columns = [' '.join(col).strip() for col in df_sca.columns.values]
    df_sca = df_sca[df_sca['Unnamed: 0_level_0 Player'] != 'Player']
    df_sca.rename(columns={
        'Unnamed: 0_level_0 Player': 'Player',
        'SCA SCA': 'Chance_Created'
    }, inplace=True)

    df_standard = tables[4]
    df_standard.columns = [' '.join(col).strip() for col in df_standard.columns.values]
    df_standard = df_standard[df_standard['Unnamed: 0_level_0 Player'] != 'Player']
    df_standard.rename(columns={
        'Unnamed: 0_level_0 Player': 'Player',
        'Standard SoT': 'Shots_on_Target'
    }, inplace=True)

    df_gk = tables[2]
    df_gk.columns = [' '.join(col).strip() for col in df_gk.columns.values]
    df_gk = df_gk[df_gk['Unnamed: 0_level_0 Player'] != 'Player']
    df_gk.rename(columns={
        'Unnamed: 0_level_0 Player': 'Player',
        'Performance Saves': 'Saves',
        'Performance GA': 'Goals_Against'
    }, inplace=True)

    df_def_misc = tables[11]
    df_def_misc.columns = [' '.join(col).strip() for col in df_def_misc.columns.values]
    df_def_misc = df_def_misc[df_def_misc['Unnamed: 0_level_0 Player'] != 'Player']
    df_def_misc.rename(columns={
        'Unnamed: 0_level_0 Player': 'Player',
        'Performance Int': 'Interceptions',
        'Performance TklW': 'Tackles_Won'
    }, inplace=True)

    df_all = df_basic.merge(df_pass[['Player', 'Passes_Completed']], on='Player', how='left')
    df_all = df_all.merge(df_sca[['Player', 'Chance_Created']], on='Player', how='left')
    df_all = df_all.merge(df_standard[['Player', 'Shots_on_Target']], on='Player', how='left')
    df_all = df_all.merge(df_def_misc[['Player', 'Interceptions', 'Tackles_Won']], on='Player', how='left')
    df_all = df_all.merge(df_gk[['Player', 'Saves', 'Goals_Against']], on='Player', how='left')
    df_all.fillna(0, inplace=True)

    # Convert numeric columns explicitly to avoid issues
    for col in ['Matches', 'Starts', 'YC', 'RC', 'OG', 'Passes_Completed', 'Chance_Created',
                'Shots_on_Target', 'Tackles_Won', 'Interceptions', 'Saves', 'Goals_Against']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0)

    df_all['Team'] = url.split('/')[-2]
    return df_all

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
    pos_count = {'GK':0, 'DF':0, 'MF':0, 'FW':0}

    def pos_key(pos):
        pos = str(pos).upper()
        if 'GK' in pos:
            return 'GK'
        elif 'DF' in pos:
            return 'DF'
        elif 'MF' in pos:
            return 'MF'
        elif 'FW' in pos:
            return 'FW'
        else:
            return None

    for idx, row in df.iterrows():
        if len(selected) == 11:
            break
        team = row['Team']
        pos = pos_key(row['Pos'])
        if pos is None:
            continue

        # Max constraints
        team_ct = count_team.get(team, 0)
        if team_ct >= 7:
            continue
        if pos == 'GK' and pos_count['GK'] >= 1:
            continue
        if pos == 'DF' and pos_count['DF'] >= 5:
            continue
        if pos == 'MF' and pos_count['MF'] >= 5:
            continue
        if pos == 'FW' and pos_count['FW'] >= 3:
            continue

        selected.append(row)
        count_team[team] = team_ct + 1
        pos_count[pos] += 1

    selected_df = pd.DataFrame(selected)

    # TODO: Implement minimum checks and fill if needed

    return selected_df[['Player', 'Pos', 'Team', 'Points']]

st.title("Premier League Dream11 Best Playing 11 Selector")

teams = list(team_urls.keys())

team1 = st.selectbox("Select Team 1", teams)
team2 = st.selectbox("Select Team 2", teams)

if st.button("Select Best Playing 11"):
    with st.spinner('Loading and processing data...'):
        df1 = load_team_data(team_urls[team1])
        df2 = load_team_data(team_urls[team2])
        df_all = pd.concat([df1, df2], ignore_index=True)
        best11 = select_best_11(df_all)
        st.table(best11)
