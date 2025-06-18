import pandas as pd


def calculate_dream11_points(df):
    """
    Calculate Dream11-style fantasy points based on provided stats.
    Omits: Goals, assists, clean sheets, penalty saves.

    Args:
        df (pd.DataFrame): DataFrame from fbref_scraper with stats.
    
    Returns:
        pd.DataFrame: Same DataFrame with added 'D11_Points' column.
    """

    # Fill NaNs with 0 for computation
    df = df.fillna(0)

    # Create a fresh column to accumulate points
    df["D11_Points"] = 0

    # Normalize position if needed
    if "Pos" in df.columns:
        df["Position"] = df["Pos"].str[:3].str.upper()
    else:
        df["Position"] = "UNK"

    # Scoring logic
    def points_per_row(row):
        pts = 0

        # Attack
        # Goal-based logic is omitted
        pts += row.get("Sh", 0) * 6  # Shots on target as proxy (FBref doesn't directly give SoT)
        pts += row.get("CrdY", 0) * -7.5
        pts += row.get("CrdR", 0) * -15
        pts += row.get("OwnG", 0) * -15
        pts += row.get("Tkl", 0) * 3.5
        pts += row.get("Int", 0) * 3.5
        pts += row.get("Clr", 0) * 1.5
        pts += row.get("Blocks", 0) * 1.5

        # Saves (Goalkeepers)
        if row["Position"] == "GK":
            pts += row.get("Saves", 0) * 4

        # Passes completed
        total_passes = row.get("Cmp", 0)  # Completed passes
        pts += (total_passes // 5) * 1

        # Chance Created — FBref approximation using Key Passes
        pts += row.get("KP", 0) * 3

        return pts

    df["D11_Points"] = df.apply(points_per_row, axis=1)

    return df
