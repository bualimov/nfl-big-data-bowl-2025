import pandas as pd
import numpy as np

# Read the results
results_df = pd.read_csv('step234/optimal_defensive_positions.csv')

# Define key formations and positions
key_formations = ['SHOTGUN', 'SINGLEBACK', 'EMPTY', 'I_FORM']
key_positions = ['CB', 'SS', 'FS', 'MLB', 'DE', 'DT']

# Create a summary table
summary_rows = []
for _, row in results_df.iterrows():
    formation = row['offenseFormation']
    alignment = row['receiverAlignment']
    
    if formation in key_formations:
        summary_row = {
            'Formation': formation,
            'Alignment': alignment
        }
        
        # Add positions
        for pos in key_positions:
            if pos in row and pd.notna(row[pos]):
                summary_row[pos] = row[pos]
            else:
                summary_row[pos] = 'N/A'
        
        summary_rows.append(summary_row)

summary_df = pd.DataFrame(summary_rows)

# Sort by formation and alignment
summary_df = summary_df.sort_values(['Formation', 'Alignment'])

# Print formatted summary
print("\nOptimal Defensive Positioning - Key Formations and Positions")
print("=" * 120)
print("\nCoordinates shown as (x, y) relative to nearest offensive player")
print("Positive x: defender is downfield of offensive player")
print("Positive y: defender is to the right of offensive player")
print("\nKey Defensive Positions:")
print("CB: Cornerback")
print("SS: Strong Safety")
print("FS: Free Safety")
print("MLB: Middle Linebacker")
print("DE: Defensive End")
print("DT: Defensive Tackle")
print("\n" + "=" * 120)
print(summary_df.to_string(index=False))

# Save summary
summary_df.to_csv('step234/optimal_defensive_positions_summary.csv', index=False)
print("\nSummary saved to step234/optimal_defensive_positions_summary.csv") 