import streamlit as st
import pandas as pd
from team_visualizer import plot_team

# Team Dictionary
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

# Fetch Function (unchanged)
def fetch_team_data(team_code, team_name):
    url = f'https://fbref.com/en/squads/{team_code}/2023-2024/c9/stats'
    tables = pd.read_html(url)

    try:
        df_basic = tables[0]
        df_basic.columns = [' '.join(col).strip() for col in df_basic.columns.values]
        df_basic = df_basic[df_basic['Unnamed: 0_level_0 Player'] != 'Player']

        rename_map = {}
        for col in df_basic.columns:
            if 'Player' in col: rename_map[col] = 'Player'
            if 'Pos' in col: rename_map[col] = 'Pos'
            if 'Starts' in col: rename_map[col] = 'Starts'
            if 'MP' in col: rename_map[col] = 'Matches'
            if 'CrdY' in col: rename_map[col] = 'YC'
            if 'CrdR' in col: rename_map[col] = 'RC'
        df_basic.rename(columns=rename_map, inplace=True)

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

        def clean_position(pos):
            pos = str(pos).upper()
            if 'GK' in pos:
                return 'GK'
            if 'FWD' in pos or 'FW' in pos:
                return 'FWD'
            elif 'MF' in pos:
                return 'MF'
            elif 'DF' in pos:
                return 'DF'
            else:
                return 'MF'

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

        df_all['Pos'] = df_all['Pos'].apply(clean_position)
        df_all['Dream11_Points'] = df_all.apply(calc_points, axis=1)
        df_all['Team'] = team_name
        df_all = df_all[~df_all['Player'].isin(['Squad Total', 'Opponent Total'])]

        return df_all[['Player', 'Team', 'Pos', 'Dream11_Points']].sort_values(by='Dream11_Points', ascending=False)

    except Exception as e:
        return pd.DataFrame({'Error': [str(e)]})

# Display Player Cards
def display_player_cards(df, color):
    for i, row in df.iterrows():
        st.markdown(
            f"""
            <div style='
                border:1px solid #ccc;
                padding:10px;
                border-radius:8px;
                margin-bottom:8px;
                background-color: {color};
            '>
                <strong>{row['Player']}</strong> — {row['Pos']} — <strong>{int(row['Dream11_Points'])} pts</strong>
            </div>
            """, unsafe_allow_html=True)

# Updated select_best_xi to enforce min and max position counts and team limits
def select_best_xi(df1, df2):
    combined = pd.concat([df1, df2], ignore_index=True)
    combined.sort_values(by='Dream11_Points', ascending=False, inplace=True)

    pos_min = {'GK': 1, 'DF': 3, 'MF': 3, 'FWD': 1}
    pos_max = {'GK': 1, 'DF': 5, 'MF': 5, 'FWD': 3}
    team_limits = {df1['Team'].iloc[0]: 7, df2['Team'].iloc[0]: 7}

    team_counts = {df1['Team'].iloc[0]: 0, df2['Team'].iloc[0]: 0}
    pos_counts = {'GK': 0, 'DF': 0, 'MF': 0, 'FWD': 0}

    best11 = []

    # Step 1: Fill minimum required players per position (top points first)
    for pos in ['GK', 'DF', 'MF', 'FWD']:
        candidates = combined[combined['Pos'] == pos]
        for _, row in candidates.iterrows():
            team = row['Team']
            if team_counts[team] >= team_limits[team]:
                continue
            if pos_counts[pos] >= pos_min[pos]:
                break  # min reached for this pos
            best11.append(row)
            team_counts[team] += 1
            pos_counts[pos] += 1

    # Step 2: Fill remaining spots (up to 11), respecting max pos and team limits
    for _, row in combined.iterrows():
        if len(best11) == 11:
            break
        if row['Player'] in [p['Player'] for p in best11]:
            continue  # already selected
        team = row['Team']
        pos = row['Pos']

        if team_counts[team] >= team_limits[team]:
            continue
        if pos_counts[pos] >= pos_max[pos]:
            continue

        best11.append(row)
        team_counts[team] += 1
        pos_counts[pos] += 1

    # Final check: minimum constraints met?
    for pos in pos_min:
        if pos_counts[pos] < pos_min[pos]:
            return pd.DataFrame({'Error': [f"Not enough players in position {pos}."]})

    if len(best11) < 11:
        return pd.DataFrame({'Error': ["Could not select 11 players satisfying constraints."]})

    return pd.DataFrame(best11)

# Helper function: add emoji suffix and keep only surname for compact display
def add_emoji_to_name(row):
    pos_icons = {
        'GK': '🧤',
        'DF': '🤼',
        'MF': '👟',
        'FWD': '⚽',
    }
    surname = row['Player'].split()[-1]
    emoji = pos_icons.get(row['Pos'], '')
    return f"{surname} {emoji}"

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🏆 Dream11 Base Point Generator (Premier League)")

tab1, tab2, tab3 = st.tabs(["🔴 Team 1", "🔵 Team 2", "⚔️ Combined XI"])

with tab1:
    team1 = st.selectbox("Choose Team 1", list(teams.keys()), key="team1")
    if st.button("Generate Top 15 - Team 1"):
        df1 = fetch_team_data(teams[team1], team1)
        st.session_state['team1_df'] = df1
        st.session_state['team1_name'] = team1

    if 'team1_df' in st.session_state:
        st.subheader(f"🔴 Top 15 - {st.session_state['team1_name']}")
        display_player_cards(st.session_state['team1_df'].head(15), "#ffe6e6")

with tab2:
    team2 = st.selectbox("Choose Team 2", list(teams.keys()), key="team2")
    if st.button("Generate Top 15 - Team 2"):
        df2 = fetch_team_data(teams[team2], team2)
        st.session_state['team2_df'] = df2
        st.session_state['team2_name'] = team2

    if 'team2_df' in st.session_state:
        st.subheader(f"🔵 Top 15 - {st.session_state['team2_name']}")
        display_player_cards(st.session_state['team2_df'].head(15), "#e6f0ff")

with tab3:
    if 'team1_df' in st.session_state and 'team2_df' in st.session_state:
        if st.button("⚔️ Generate Best Combined XI"):
            combined = select_best_xi(st.session_state['team1_df'], st.session_state['team2_df'])
            if 'Error' in combined.columns:
                st.error(combined.iloc[0]['Error'])
            else:
                combined['PlayerWithEmoji'] = combined.apply(add_emoji_to_name, axis=1)
                combined['TeamColor'] = combined['Team'].apply(
                    lambda x: '🔴 ' + x if x == st.session_state['team1_name'] else '🔵 ' + x
                )
                st.subheader("💥 Best Combined XI")
                st.dataframe(
                    combined[['PlayerWithEmoji', 'TeamColor', 'Pos', 'Dream11_Points']]
                    .rename(columns={'PlayerWithEmoji': 'Player', 'TeamColor': 'Team'})
                )

                # Plot visual of the team
                fig = plot_team(combined)
                st.pyplot(fig)
