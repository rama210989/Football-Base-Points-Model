import pandas as pd
from itertools import combinations


def select_best_11(df):
    """
    Selects the best 11 players from a combined team DataFrame with D11_Points.
    Constraints:
      - 11 players total
      - Max 7 from one real team
      - Formation: 1 GK, 3–5 DEF, 3–5 MID, 1–3 FWD
    Args:
        df (pd.DataFrame): Combined player stats with columns: 'Player', 'Pos', 'D11_Points', 'Squad'
    Returns:
        pd.DataFrame: Best 11 player selection
    """

    # Normalize positions
    df = df.copy()
    df["Position"] = df["Pos"].str.upper().str[:3]

    # Simplify to one role per player (basic logic)
    def map_pos(pos):
        if "GK" in pos:
            return "GK"
        elif any(p in pos for p in ["DEF", "DF"]):
            return "DEF"
        elif any(p in pos for p in ["MID", "MF"]):
            return "MID"
        else:
            return "FWD"
    df["Role"] = df["Position"].apply(map_pos)

    # Filter players by roles
    gk_pool = df[df["Role"] == "GK"].nlargest(3, "D11_Points")
    def_pool = df[df["Role"] == "DEF"].nlargest(10, "D11_Points")
    mid_pool = df[df["Role"] == "MID"].nlargest(10, "D11_Points")
    fwd_pool = df[df["Role"] == "FWD"].nlargest(6, "D11_Points")

    best_team = None
    best_score = -float("inf")

    # Try all valid combinations
    for def_n in range(3, 6):
        for mid_n in range(3, 6):
            for fwd_n in range(1, 4):
                if def_n + mid_n + fwd_n + 1 != 11:
                    continue

                for gk in gk_pool.itertuples():
                    for defs in combinations(def_pool.itertuples(), def_n):
                        for mids in combinations(mid_pool.itertuples(), mid_n):
                            for fwds in combinations(fwd_pool.itertuples(), fwd_n):
                                team = [gk] + list(defs) + list(mids) + list(fwds)
                                team_df = pd.DataFrame(team)

                                # Check team size
                                if len(team_df) != 11:
                                    continue

                                # Enforce max 7 from one real-life team
                                team_counts = pd.Series([p.Squad for p in team]).value_counts()
                                if any(team_counts > 7):
                                    continue

                                # Score the team
                                total_score = sum(p.D11_Points for p in team)
                                if total_score > best_score:
                                    best_score = total_score
                                    best_team = team_df.copy()

    if best_team is None:
        raise ValueError("No valid team combination found.")

    best_team["Player"] = best_team["Player"].apply(lambda x: x.strip())
    best_team = best_team[["Player", "Role", "Squad", "D11_Points"]].sort_values(by="D11_Points", ascending=False)
    best_team.reset_index(drop=True, inplace=True)
    return best_team
