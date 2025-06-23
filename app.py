import streamlit as st
import pandas as pd

teams = {
    'Arsenal': '18bb7c10',
    'Aston Villa': '8602292d',
    'Bournemouth': '4ba7cbea',
    'Brentford': 'cd051869',
    'Brighton': 'd07537b9',
    'Burnley': '943e8050',
    'Chelsea': 'cff3d9bb',
    'Crystal Palace': '47c64c55',
    'Everton': 'd3fd31cc',
    'Fulham': 'fd962109',
    'Liverpool': '822bd0ba',
    'Luton Town': 'e297cd13',
    'Manchester City': 'b8fd03ef',
    'Manchester United': '19538871',
    'Newcastle United': 'b2b47a98',
    'Nottingham Forest': 'e4a775cb',
    'Sheffield United': '1df6b87e',
    'Tottenham': '361ca564',
    'West Ham': '7c21e445',
    'Wolves': '8cec06e1'
}

def fetch_team_data(team_code):
    url = f'https://fbref.com/en/squads/{team_code}/2023-2024/c9/stats'
    tables = pd.read_html(url)

    try:
        # Basic stats
        df_basic = tables[0]
        df_basic.columns = [' '.join(col).strip() for col in df_basic.columns.values]
        df_basic = df_basic[df_basic['Unnamed: 0_level_0 Player'] != 'Player']
        df_basic.rename(columns={
            'Unnamed: 0_level_0 Player': 'Player',
            'Unnamed: 2_level_0 Pos': 'Pos',
            'Playing Time Starts': 'Starts',
            'Performance CrdY': 'YC',
            'Performance CrdR': 'RC',
            'Unnamed: 4_level_0 MP': 'Matches'
        }, inplace=True)

        # Defensive + Misc
        df_def_misc = tables[11]
        df_def_misc.columns = [' '.join(col).strip() for col in df_def_misc.columns.values]
        df_def_misc = df_def_misc[df_def_misc['Unnamed: 0_level_0 Player'] != 'Player']
        df_def_misc.rename(columns={
            'Unnamed: 0_level_0 Player': 'Player',
            'Performance Int': 'Interceptions',
            'Performance TklW': 'Tackles_Won',
            'Performance OG': 'OG'
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

        df_all = df_basic.merge(df_pass[['Player', 'Passes_Completed']], on='Player', how='left')
        df_all = df_all.merge(df_sca[['Player', 'Chance_Created']], on='Player', how='left')
        df_all = df_all.merge(df_standard[['Player', 'Shots_on_Target']], on='Player', how='left')
        df_all = df_all.merge(df_def_misc[['Player', 'Interceptions', 'Tackles_Won', 'OG']], on='Player', how='left')
        df_all = df_all.merge(df_gk[['Player', 'Saves', 'Goals_Against']], on='Player', how='left')

        df_all.fillna(0, inplace=True)

        def calc_points(row):
            points = 0
            points += row['Chance_Created'] * 3
            points += row['Shots_on_Target'] * 6
            points += (row['Passes_Completed'] // 5) * 1
            points += row['Tackles_Won'] * 4
            points += row['Interceptions'] * 4
            points += row['Saves'] * 6
            points += (row['Starts'] > 0) * 4
            points += (row['Matches'] - row['Starts']) * 2
            points -= row['YC'] * 4
            points -= row['RC'] * 10
            points -= row['OG'] * 8
            if row['Pos'] in ['GK', 'DF']:
                points -= row['Goals_Against'] * 2
            return points

        df_all['Dream11_Points'] = df_all.apply(calc_points, axis=1)
        df_all = df_all[~df_all['Player'].isin(['Squad Total', 'Opponent Total'])]
        return df_all[['Player', 'Pos', 'Dream11_Points']].sort_values(by='Dream11_Points', ascending=False).head(15)

    except Exception as e:
        return pd.DataFrame({'Error': [str(e)]})


st.set_page_config(layout="wide")
st.title("🏆 Dream11 Best 15 Generator (Premier League)")

col1, col2 = st.columns(2)

with col1:
    team1 = st.selectbox("🔴 Select Team 1", list(teams.keys()), key="team1")
    if st.button("Generate Top 15 - Team 1"):
        st.session_state['team1_df'] = fetch_team_data(teams[team1])
        st.session_state['team1_name'] = team1

with col2:
    team2 = st.selectbox("🔵 Select Team 2", list(teams.keys()), key="team2")
    if st.button("Generate Top 15 - Team 2"):
        st.session_state['team2_df'] = fetch_team_data(teams[team2])
        st.session_state['team2_name'] = team2

# Display both results side-by-side if available
if 'team1_df' in st.session_state:
    st.subheader(f"🔴 Top 15 Players - {st.session_state['team1_name']}")
    st.dataframe(st.session_state['team1_df'])

if 'team2_df' in st.session_state:
    st.subheader(f"🔵 Top 15 Players - {st.session_state['team2_name']}")
    st.dataframe(st.session_state['team2_df'])
