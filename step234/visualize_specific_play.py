import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_tracking_data(week):
    return pd.read_csv(f'tracking_week_{week}.csv')

def load_plays():
    return pd.read_csv('plays.csv')

def load_players():
    return pd.read_csv('players.csv')

def load_optimal_positions():
    try:
        return pd.read_csv('step234/optimal_defensive_positions.csv')
    except FileNotFoundError:
        return None

def find_valid_play(tracking_data, plays, play_type='Any'):
    if play_type == 'Passing':
        valid_plays = plays[plays['passResult'].notna()]
    else:
        valid_plays = plays
        
    for _, play in valid_plays.iterrows():
        play_data = tracking_data[
            (tracking_data['gameId'] == play['gameId']) & 
            (tracking_data['playId'] == play['playId'])
        ]
        if len(play_data) > 0:
            return play['gameId'], play['playId']
    return None, None

def get_last_pre_snap_frame(play_data):
    pre_snap = play_data[play_data['frameType'] == 'BEFORE_SNAP']
    if len(pre_snap) == 0:
        return None
    return pre_snap['frameId'].max()

def plot_field():
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Field dimensions
    field_length = 120
    field_width = 53.3
    
    # Draw the field
    ax.plot([0, field_length], [0, 0], 'white')
    ax.plot([0, field_length], [field_width, field_width], 'white')
    ax.plot([0, 0], [0, field_width], 'white')
    ax.plot([field_length, field_length], [0, field_width], 'white')
    
    # Set field color
    ax.set_facecolor('darkgreen')
    
    # Set yard lines
    for yard in range(0, 121, 10):
        ax.plot([yard, yard], [0, field_width], 'white', alpha=0.4)
        
    ax.set_xlim(-5, field_length + 5)
    ax.set_ylim(-5, field_width + 5)
    
    return fig, ax

def plot_players(ax, frame_data, optimal_positions=None, players_data=None):
    # Merge with players data if provided
    if players_data is not None:
        frame_data = frame_data.merge(
            players_data[['nflId', 'position']], 
            on='nflId',
            how='left'
        )
    
    # Plot offensive players in red
    offense = frame_data[frame_data['club'] == frame_data['club'].iloc[0]]
    ax.scatter(offense['x'], offense['y'], c='red', s=100, label='Offense')
    
    # Plot defensive players in blue
    defense = frame_data[frame_data['club'] != frame_data['club'].iloc[0]]
    ax.scatter(defense['x'], defense['y'], c='blue', s=100, label='Defense')
    
    if optimal_positions is not None:
        # Plot optimal defensive positions in cyan
        ax.scatter(
            optimal_positions['x'], 
            optimal_positions['y'],
            c='cyan',
            s=150,
            alpha=0.5,
            label='Optimal Defense'
        )
        
        # Add position labels for optimal positions
        for _, pos in optimal_positions.iterrows():
            ax.annotate(
                pos['position'],
                (pos['x'], pos['y']),
                color='cyan',
                ha='center',
                va='center'
            )
    
    # Add jersey numbers for players (excluding the ball)
    for _, player in frame_data.iterrows():
        if pd.notna(player['jerseyNumber']):
            ax.annotate(
                str(int(player['jerseyNumber'])), 
                (player['x'], player['y']),
                color='white',
                ha='center',
                va='center'
            )
    
    ax.legend()

def main():
    # Load data
    tracking_data = load_tracking_data(1)
    plays = load_plays()
    players = load_players()
    optimal_positions = load_optimal_positions()
    
    print(f"Loaded {len(tracking_data)} tracking records")
    print(f"Loaded {len(plays)} plays")
    print(f"Loaded {len(players)} players")
    
    # Process regular play
    print("\nProcessing regular play...")
    print("Looking for a valid play...")
    game_id, play_id = find_valid_play(tracking_data, plays)
    
    if game_id and play_id:
        print(f"Found valid play: {play_id} from game {game_id}")
        print("Play type: Any")
        
        play_data = tracking_data[
            (tracking_data['gameId'] == game_id) & 
            (tracking_data['playId'] == play_id)
        ]
        
        last_frame = get_last_pre_snap_frame(play_data)
        if last_frame:
            frame_data = play_data[play_data['frameId'] == last_frame]
            
            fig, ax = plot_field()
            plot_players(ax, frame_data, players_data=players)
            plt.title(f'Play {play_id} - Last Pre-snap Frame')
            plt.savefig('step234/play_analysis.png')
            plt.close()
    
    # Process passing play
    print("\nProcessing passing play...")
    print("Looking for a valid play...")
    print("Filtering for passing plays...")
    game_id, play_id = find_valid_play(tracking_data, plays, play_type='Passing')
    
    if game_id and play_id:
        print(f"Found valid play: {play_id} from game {game_id}")
        print("Play type: Passing")
        
        play_data = tracking_data[
            (tracking_data['gameId'] == game_id) & 
            (tracking_data['playId'] == play_id)
        ]
        
        last_frame = get_last_pre_snap_frame(play_data)
        if last_frame:
            frame_data = play_data[play_data['frameId'] == last_frame]
            
            # Create regular version
            fig, ax = plot_field()
            plot_players(ax, frame_data, players_data=players)
            plt.title(f'Passing Play {play_id} - Last Pre-snap Frame')
            plt.savefig('step234/passing_play_analysis.png')
            plt.close()
            
            # Create optimal-only version
            print("\nCreating optimal-only version of passing play...")
            if optimal_positions is not None:
                fig, ax = plot_field()
                plot_players(ax, frame_data, optimal_positions, players_data=players)
                plt.title(f'Passing Play {play_id} - With Optimal Positions')
                plt.savefig('step234/passing_play_analysis_optimal.png')
                plt.close()
            else:
                print("No optimal positions data found")

if __name__ == "__main__":
    main() 