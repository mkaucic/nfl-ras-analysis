import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_positions():
    print("Performing position-specific analysis...")
    
    # Create output directory
    os.makedirs('../../backend/analysis/visualizations/positions', exist_ok=True)
    
    # Load the data
    try:
        df = pd.read_csv('../../backend/data/pro_bowlers_ras.csv')
        print(f"Loaded data for {len(df)} players")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Convert RAS to numeric
    if 'RAS' in df.columns:
        df['RAS_numeric'] = pd.to_numeric(df['RAS'], errors='coerce')
    
    # Convert Pro Bowls to numeric
    pro_bowl_cols = ['Pro Bowls', 'ProBowls', 'Pro_Bowls']
    for col in pro_bowl_cols:
        if col in df.columns:
            df['Pro_Bowl_Count'] = pd.to_numeric(df[col], errors='coerce')
            break
    
    # Handle position
    pos_col = None
    for col in ['Position', 'Pos']:
        if col in df.columns:
            pos_col = col
            break
    
    if not pos_col:
        print("No position column found")
        return
    
    # Filter out DB position as requested earlier
    df = df[df[pos_col] != 'DB']
    
    # Get unique positions
    positions = df[pos_col].unique()
    print(f"Analyzing {len(positions)} positions: {positions}")
    
    # Create position summary data
    position_stats = []
    for position in positions:
        pos_data = df[df[pos_col] == position]
        
        if len(pos_data) < 3:  # Skip positions with too few players
            continue
            
        avg_ras = pos_data['RAS_numeric'].mean()
        avg_pro_bowls = pos_data['Pro_Bowl_Count'].mean()
        total_pro_bowls = pos_data['Pro_Bowl_Count'].sum()
        multi_pb_rate = (pos_data['Pro_Bowl_Count'] > 1).mean() * 100
        
        # RAS distribution visualization
        plt.figure(figsize=(10, 6))
        sns.histplot(pos_data['RAS_numeric'].dropna(), bins=10, kde=True)
        plt.title(f'RAS Distribution for {position}')
        plt.xlabel('Relative Athletic Score (RAS)')
        plt.ylabel('Count')
        plt.savefig(f'../../backend/analysis/visualizations/positions/{position}_ras_distribution.png')
        plt.close()
        
        # RAS vs Pro Bowls scatter plot
        plt.figure(figsize=(10, 6))
        sns.regplot(x='RAS_numeric', y='Pro_Bowl_Count', data=pos_data, scatter_kws={'alpha':0.5})
        plt.title(f'RAS vs Pro Bowl Selections for {position}')
        plt.xlabel('Relative Athletic Score (RAS)')
        plt.ylabel('Pro Bowl Selections')
        plt.savefig(f'../../backend/analysis/visualizations/positions/{position}_ras_vs_probowls.png')
        plt.close()
        
        # Add to position stats
        position_stats.append({
            'Position': position,
            'PlayerCount': len(pos_data),
            'AvgRAS': avg_ras,
            'AvgProBowls': avg_pro_bowls,
            'TotalProBowls': total_pro_bowls,
            'MultiProBowlRate': multi_pb_rate
        })
    
    # Create position summary dataframe
    position_df = pd.DataFrame(position_stats)
    
    # Save for frontend
    position_df.to_json('../../frontend/public/data/position_stats.json', orient='records')
    print("Position-specific analysis complete and saved")
    
    # Create position comparison chart
    plt.figure(figsize=(12, 8))
    chart_data = position_df.sort_values('AvgRAS', ascending=False)
    sns.barplot(x='Position', y='AvgRAS', data=chart_data)
    plt.title('Average RAS by Position')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../../backend/analysis/visualizations/position_ras_comparison.png')
    plt.close()
    
    # Create multi-Pro Bowl rate comparison
    plt.figure(figsize=(12, 8))
    chart_data = position_df.sort_values('MultiProBowlRate', ascending=False)
    sns.barplot(x='Position', y='MultiProBowlRate', data=chart_data)
    plt.title('Multiple Pro Bowl Rate by Position (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../../backend/analysis/visualizations/position_probowl_rate.png')
    plt.close()

if __name__ == "__main__":
    analyze_positions()