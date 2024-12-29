import pandas as pd
import numpy as np

# Read the plays data
plays_df = pd.read_csv('plays.csv')

# Analyze offensive formations
formation_analysis = plays_df['offenseFormation'].value_counts()
formation_percentages = (formation_analysis / len(plays_df) * 100).round(1)

# Create formations DataFrame
formations_data = {
    'Count': formation_analysis,
    'Percentage': formation_percentages
}
formations_df = pd.DataFrame(formations_data)

# Add descriptions for known formations
formation_descriptions = {
    'SHOTGUN': 'Pass-heavy, better QB visibility',
    'SINGLEBACK': 'Balanced run/pass option',
    'EMPTY': 'Maximum passing options',
    'I_FORM': 'Power running plays',
    'PISTOL': 'Hybrid run/pass versatility',
    'JUMBO': 'Short-yardage/goal line',
    'WILDCAT': 'Specialty/misdirection'
}
formations_df['Primary Usage'] = formations_df.index.map(lambda x: formation_descriptions.get(x, 'Specialty formation'))

# Analyze receiver alignments
alignment_analysis = plays_df['receiverAlignment'].value_counts()
alignment_percentages = (alignment_analysis / len(plays_df) * 100).round(1)

# Create alignments DataFrame
alignments_data = {
    'Count': alignment_analysis,
    'Percentage': alignment_percentages
}
alignments_df = pd.DataFrame(alignments_data)

# Add descriptions for known alignments
alignment_descriptions = {
    '2x2': 'Two receivers on each side',
    '3x1': 'Three receivers one side, one opposite',
    '2x1': 'Two receivers one side, one opposite',
    '3x2': 'Three receivers one side, two opposite',
    '1x1': 'One receiver on each side',
    '4x1': 'Four receivers one side',
    '2x0': 'Two receivers one side',
    '3x0': 'Three receivers one side',
    '1x0': 'One receiver one side',
    '4x2': 'Four receivers one side, two opposite'
}
alignments_df['Description'] = alignments_df.index.map(lambda x: alignment_descriptions.get(x, 'Specialty alignment'))

# Analyze formation-alignment combinations
formation_alignment_counts = plays_df.groupby(['offenseFormation', 'receiverAlignment']).size()
top_combinations = formation_alignment_counts.nlargest(10)

combinations_df = pd.DataFrame(top_combinations).reset_index()
combinations_df.columns = ['Formation', 'Alignment', 'Count']
combinations_df['Percentage'] = (combinations_df['Count'] / len(plays_df) * 100).round(1)

# Print results with nice formatting
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)

print("\nOffensive Formation Analysis")
print("=" * 100)
print("\nTable 1: Offensive Formations")
print(formations_df.to_string())

print("\n\nTable 2: Receiver Alignments")
print("=" * 100)
print(alignments_df.to_string())

print("\n\nTable 3: Top Formation-Alignment Combinations")
print("=" * 100)
print(combinations_df.to_string())

# Save results to CSV files for further analysis if needed
formations_df.to_csv('formation_analysis.csv')
alignments_df.to_csv('alignment_analysis.csv')
combinations_df.to_csv('formation_alignment_combinations.csv') 