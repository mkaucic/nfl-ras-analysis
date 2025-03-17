import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# Make sure the analysis directory exists
os.makedirs('../../backend/analysis', exist_ok=True)

def analyze_ras_data():
    print("Starting RAS data analysis...")
    
    # First try the detailed file, if that doesn't work use the basic file
    try:
        print("Trying to load detailed data...")
        df = pd.read_csv('../../backend/data/pro_bowlers_ras_detailed.csv')
        print(f"Loaded detailed data for {len(df)} players")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("Detailed data not available. Loading basic data instead...")
        try:
            df = pd.read_csv('../../backend/data/pro_bowlers_ras.csv')
            print(f"Loaded basic data for {len(df)} players")
        except FileNotFoundError:
            print("Error: No data files found. Please run collect_data.py first.")
            return
    
    # Convert columns to appropriate types
    print("Converting data types...")
    
    # Handle RAS column
    if 'RAS' in df.columns:
        df['RAS_numeric'] = pd.to_numeric(df['RAS'], errors='coerce')
    else:
        print("Warning: RAS column not found in data")
        df['RAS_numeric'] = np.nan
    
    # Handle Pro Bowls column
    pro_bowl_col = None
    for col in ['Pro_Bowls', 'ProBowls', 'Pro Bowls']:
        if col in df.columns:
            pro_bowl_col = col
            break
    
    if pro_bowl_col:
        df['Pro_Bowls_numeric'] = pd.to_numeric(df[pro_bowl_col], errors='coerce')
    else:
        print("Warning: Pro Bowl column not found in data")
        df['Pro_Bowls_numeric'] = np.nan
    
    # Handle Position column
    pos_col = None
    for col in ['Position', 'Pos']:
        if col in df.columns:
            pos_col = col
            break
    
    if not pos_col:
        print("Warning: Position column not found in data")
        df['Position'] = 'Unknown'
    else:
        df['Position'] = df[pos_col]
    
    # Handle Player/Name column
    player_col = None
    for col in ['Player', 'Name']:
        if col in df.columns:
            player_col = col
            break
    
    if not player_col:
        print("Warning: Player/Name column not found in data")
        df['Player'] = 'Unknown'
    else:
        # If player name is stored as a dictionary (with text and link), extract just the text
        if isinstance(df[player_col].iloc[0], dict) and 'text' in df[player_col].iloc[0]:
            df['Player'] = df[player_col].apply(lambda x: x['text'] if isinstance(x, dict) and 'text' in x else x)
            # Also save the link if available
            df['Profile_URL'] = df[player_col].apply(lambda x: x['link'] if isinstance(x, dict) and 'link' in x else None)
        else:
            df['Player'] = df[player_col]
    
    # Basic statistics
    print("\nCalculating statistics...")
    ras_stats = df['RAS_numeric'].describe()
    print("\nRAS Statistics:")
    print(ras_stats)

    # Skip correlation analysis if missing data
    if not df['RAS_numeric'].isna().all() and not df['Pro_Bowls_numeric'].isna().all():
        # Correlation between RAS and Pro Bowl appearances
        correlation = df['RAS_numeric'].corr(df['Pro_Bowls_numeric'])
        print(f"\nCorrelation between RAS and Pro Bowl appearances: {correlation:.4f}")

        # Calculate p-value if we have enough data
        if len(df['RAS_numeric'].dropna()) > 2 and len(df['Pro_Bowls_numeric'].dropna()) > 2:
            valid_data = df.dropna(subset=['RAS_numeric', 'Pro_Bowls_numeric'])
            if len(valid_data) > 2:  # Need at least 3 points for regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    valid_data['RAS_numeric'], 
                    valid_data['Pro_Bowls_numeric']
                )
                print(f"P-value: {p_value:.4f}")
    
    # Group by position (if position data is available)
    if 'Position' in df.columns and not df['Position'].isna().all():
        try:
            position_stats = df.groupby('Position').agg({
                'RAS_numeric': ['mean', 'std', 'count'],
                'Pro_Bowls_numeric': ['mean', 'sum']
            }).reset_index()
            print("\nPosition-wise statistics:")
            print(position_stats)
        except Exception as e:
            print(f"Error calculating position stats: {e}")

    # Create visualizations
    print("\nGenerating visualizations...")
    
    try:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='RAS_numeric', y='Pro_Bowls_numeric', hue='Position')
        plt.title('RAS vs Pro Bowl Appearances')
        plt.xlabel('Relative Athletic Score (RAS)')
        plt.ylabel('Pro Bowl Appearances')
        plt.savefig('../../backend/analysis/ras_vs_probowls.png')
        print("Created RAS vs Pro Bowls scatter plot")
    except Exception as e:
        print(f"Error creating scatter plot: {e}")

    # Position-wise RAS distribution
    try:
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, x='Position', y='RAS_numeric')
        plt.title('RAS Distribution by Position')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('../../backend/analysis/ras_by_position.png')
        print("Created RAS by Position box plot")
    except Exception as e:
        print(f"Error creating box plot: {e}")

    # Export processed data for frontend
    print("\nPreparing data for frontend...")
    
    # Select columns for export, handling missing columns gracefully
    columns_to_export = []
    for col in ['Player', 'Position', 'RAS_numeric', 'Pro_Bowls_numeric', 'College', 'Draft', 'Profile_URL']:
        if col in df.columns:
            columns_to_export.append(col)
    
    df_export = df[columns_to_export]
    
    # Make sure the frontend public/data directory exists
    os.makedirs('../../frontend/public/data', exist_ok=True)
    
    df_export.to_json('../../frontend/public/data/processed_data.json', orient='records')
    print("Exported processed data for frontend")
    
    print("Analysis complete!")

if __name__ == "__main__":
    analyze_ras_data()