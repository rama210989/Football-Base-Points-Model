import matplotlib.pyplot as plt

def plot_team(df_best11):
    pos_coords = {
        'GK': [(0.5, 0.05)],
        'DF': [(0.15, 0.25), (0.35, 0.25), (0.65, 0.25), (0.85, 0.25), (0.5, 0.35)],
        'MF': [(0.15, 0.5), (0.35, 0.5), (0.65, 0.5), (0.85, 0.5), (0.5, 0.6)],
        'FWD': [(0.3, 0.75), (0.5, 0.8), (0.7, 0.75)]
    }

    pos_icons = {
        'GK': '🧤',
        'DF': '🤼',
        'MF': '👟',
        'FWD': '⚽',
    }

    fig, ax = plt.subplots(figsize=(8, 12))

    # Set the figure background color to green (pitch)
    fig.patch.set_facecolor('forestgreen')

    # Set the axes background color (the "pitch" area)
    ax.set_facecolor('forestgreen')

    pitch_color = 'white'
    ax.plot([0, 1], [0, 0], color=pitch_color)
    ax.plot([0, 1], [1, 1], color=pitch_color)
    ax.plot([0, 0], [0, 1], color=pitch_color)
    ax.plot([1, 1], [0, 1], color=pitch_color)
    ax.plot([0, 1], [0.5, 0.5], color=pitch_color)
    circle = plt.Circle((0.5, 0.5), 0.1, color=pitch_color, fill=False, linewidth=2)
    ax.add_patch(circle)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis('off')

    pos_count = {'GK': 0, 'DF': 0, 'MF': 0, 'FWD': 0}

    for _, row in df_best11.iterrows():
        pos = row['Pos']
        idx = pos_count[pos] % len(pos_coords[pos])
        x, y = pos_coords[pos][idx]
        pos_count[pos] += 1

        # Use PlayerWithEmoji column for compact surname + emoji display on pitch
        player_text = row.get('PlayerWithEmoji', row['Player'])

        ax.text(
            x, y,
            f"{player_text}\n{int(row['Dream11_Points'])} pts",
            ha='center', va='center',
            fontsize=10,
            color='yellow',
            bbox=dict(facecolor='blue', alpha=0.75, boxstyle='round,pad=0.5')
        )

    ax.set_title("Dream11 Best Combined XI", fontsize=18, color='white', pad=20)

    plt.tight_layout()
    return fig
