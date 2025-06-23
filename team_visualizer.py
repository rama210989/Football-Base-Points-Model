import matplotlib.pyplot as plt

def plot_team(df_best11):
    """
    Plot a simple football pitch layout with player names, points, and position icons.
    Assumes df_best11 has columns: 'Player', 'Pos', 'Dream11_Points'
    """
    # Coordinates roughly mapping standard 4-4-2/4-3-3-ish formation on a 0-1 scale
    pos_coords = {
        'GK': [(0.5, 0.05)],
        'DF': [(0.15, 0.25), (0.35, 0.25), (0.65, 0.25), (0.85, 0.25), (0.5, 0.35)],
        'MF': [(0.15, 0.5), (0.35, 0.5), (0.65, 0.5), (0.85, 0.5), (0.5, 0.6)],
        'FWD': [(0.3, 0.75), (0.5, 0.8), (0.7, 0.75)]
    }

    # Position icons per role
    pos_icons = {
        'GK': '🧤',
        'DF': '🤼',
        'MF': '👟',
        'FWD': '⚽',
    }

    # Start plotting
    fig, ax = plt.subplots(figsize=(8, 12))
    ax.set_facecolor('forestgreen')

    # Draw pitch outline and markings
    pitch_color = 'white'
    ax.plot([0, 1], [0, 0], color=pitch_color)  # bottom line
    ax.plot([0, 1], [1, 1], color=pitch_color)  # top line
    ax.plot([0, 0], [0, 1], color=pitch_color)  # left line
    ax.plot([1, 1], [0, 1], color=pitch_color)  # right line
    ax.plot([0, 1], [0.5, 0.5], color=pitch_color)  # halfway line
    circle = plt.Circle((0.5, 0.5), 0.1, color=pitch_color, fill=False, linewidth=2)
    ax.add_patch(circle)

    # Hide axes
    ax.axis('off')

    # Track position counters (to cycle if more players than coords)
    pos_count = {'GK': 0, 'DF': 0, 'MF': 0, 'FWD': 0}

    for _, row in df_best11.iterrows():
        pos = row['Pos']
        idx = pos_count[pos] % len(pos_coords[pos])
        x, y = pos_coords[pos][idx]
        pos_count[pos] += 1

        icon = pos_icons.get(pos, '')

        # Display player name, points, and icon
        ax.text(
            x, y,
            f"{icon} {row['Player']}\n{int(row['Dream11_Points'])} pts",
            ha='center', va='center',
            fontsize=10,
            color='yellow',
            bbox=dict(facecolor='blue', alpha=0.75, boxstyle='round,pad=0.5')
        )

    ax.set_title("Dream11 Best Combined XI", fontsize=18, color='white', pad=20)
    plt.tight_layout()
    return fig
