import pandas as pd
import numpy as np
import os
import json
import re

def analyze_measurement_correlations():
    print("Analyzing correlations between athletic measurements and Pro Bowl success...")
    
    # Create output directory
    os.makedirs('../../backend/analysis/visualizations', exist_ok=True)
    os.makedirs('../../frontend/public/data', exist_ok=True)
    
    # Try to load the detailed measurements
    try:
        # Try JSON first as it preserves data types better
        if os.path.exists('../../backend/data/player_detailed_measurements.json'):
            df = pd.read_json('../../backend/data/player_detailed_measurements.json')
        else:
            df = pd.read_csv('../../backend/data/player_detailed_measurements.csv')
            
        print(f"Loaded detailed measurements for {len(df)} players")
        print(f"Available columns: {list(df.columns)}")
    except Exception as e:
        print(f"Detailed measurements not available: {e}")
        print("Falling back to basic data")
        
        try:
            df = pd.read_csv('../../backend/data/pro_bowlers_ras.csv')
            print(f"Loaded basic data for {len(df)} players")
        except Exception as e:
            print(f"Error loading data: {e}")
            return
    
    # Convert measurements to numeric values
    measurement_cols = []
    for col in df.columns:
        # Skip non-measurement columns
        if col in ['player_name', 'position', 'profile_url', 'player_id']:
            continue
            
        # Process the column if it might contain a measurement
        try:
            # Extract numeric values using regex
            if df[col].dtype == 'object':
                # Create a new numeric column
                numeric_col = f"{col}_numeric"
                
                # Extract numbers from strings like "4.50 seconds" or "35.5 inches"
                df[numeric_col] = df[col].astype(str).apply(
                    lambda x: re.search(r'(\d+\.\d+|\d+)', x).group(1) if re.search(r'(\d+\.\d+|\d+)', x) else np.nan
                ).astype(float)
                
                measurement_cols.append(numeric_col)
            else:
                measurement_cols.append(col)
        except Exception as e:
            print(f"Could not convert column {col} to numeric: {e}")
    
    print(f"Processed {len(measurement_cols)} numeric measurement columns")
    
    # Handle Pro Bowl data
    if 'pro_bowls' in df.columns:
        df['pro_bowls_numeric'] = pd.to_numeric(df['pro_bowls'], errors='coerce')
        df['multiple_pro_bowls'] = (df['pro_bowls_numeric'] > 1).astype(int)
        success_cols = ['pro_bowls_numeric', 'multiple_pro_bowls']
    else:
        # Try to find Pro Bowl columns in the original data
        success_cols = []
        for col in ['Pro_Bowls', 'ProBowls', 'Pro Bowls']:
            if col in df.columns:
                df['pro_bowls_numeric'] = pd.to_numeric(df[col], errors='coerce')
                df['multiple_pro_bowls'] = (df['pro_bowls_numeric'] > 1).astype(int)
                success_cols = ['pro_bowls_numeric', 'multiple_pro_bowls']
                break
    
    if not success_cols:
        print("No Pro Bowl data found, cannot analyze correlations with success")
        return
    
    # Handle RAS score
    ras_col = None
    for col in ['ras_score', 'RAS']:
        if col in df.columns:
            df['ras_numeric'] = pd.to_numeric(df[col], errors='coerce')
            ras_col = 'ras_numeric'
            break
    
    if ras_col:
        measurement_cols.append(ras_col)
    
    # Calculate correlations
    analysis_cols = measurement_cols + success_cols
    
    # Filter out columns with too many missing values
    valid_cols = []
    for col in analysis_cols:
        if col in df.columns and df[col].notna().sum() > len(df) * 0.1:  # At least 10% of values are not NA
            valid_cols.append(col)
    
    print(f"Using {len(valid_cols)} columns for correlation analysis")
    
    if len(valid_cols) > 2:  # Need at least measurements + success metric
        # Calculate correlations
        corr_df = df[valid_cols].corr()
        
        # Optional: Sort columns to group similar measurements
        # This makes the heatmap more interpretable
        try:
            # Group metrics (RAS, pro bowls at the end)
            important_cols = ['ras_numeric', 'pro_bowls_numeric', 'multiple_pro_bowls']
            present_important = [col for col in important_cols if col in corr_df.columns]
            other_cols = [col for col in corr_df.columns if col not in important_cols]
            
            # Sort measurement columns alphabetically 
            other_cols.sort()
            
            # New column order: measurements first, then RAS and success metrics
            new_col_order = other_cols + present_important
            corr_df = corr_df.loc[new_col_order, new_col_order]
        except Exception as e:
            print(f"Error sorting correlation columns: {e}")
        
        # Convert correlation to serializable format
        corr_dict = {}
        for i, col1 in enumerate(corr_df.columns):
            corr_dict[col1] = {}
            for j, col2 in enumerate(corr_df.columns):
                corr_dict[col1][col2] = corr_df.iloc[i, j]
        
        # Save to JSON
        with open('../../frontend/public/data/measurement_correlation.json', 'w') as f:
            json.dump(corr_dict, f)
            
        # Also save a CSV version
        corr_df.to_csv('../../backend/analysis/visualizations/measurement_correlation.csv')
        
        print("Correlation data saved successfully")
        
        # Create a focused correlation analysis just with success metrics
        success_corr = corr_df[present_important].drop(present_important)
        
        # Save this simpler correlation data
        success_corr.to_csv('../../backend/analysis/visualizations/success_correlation.csv')
        
        # Create a dictionary version with cleaner keys for display
        success_dict = {}
        for idx, row in success_corr.iterrows():
            # Create a cleaner display name
            display_name = idx.replace('_numeric', '').replace('_', ' ').title()
            
            success_dict[display_name] = {}
            for col in row.index:
                # Clean up column name too
                col_display = col.replace('_numeric', '').replace('_', ' ').title()
                success_dict[display_name][col_display] = row[col]
        
        with open('../../frontend/public/data/success_correlation.json', 'w') as f:
            json.dump(success_dict, f)
        
        print("Success correlation data saved")
    else:
        print("Not enough valid columns for correlation analysis")

if __name__ == "__main__":
    analyze_measurement_correlations()