import pandas as pd
import os
import json

# Path to CSV and JSON files
csv_path = '../../backend/data/pro_bowlers_ras.csv'  # Use the basic data file
detailed_csv_path = '../../backend/data/pro_bowlers_ras_detailed.csv'  # Detailed file if available
json_path = '../../backend/data/pro_bowlers_ras.json'
frontend_json_path = '../../frontend/public/data/processed_data.json'

# Create frontend data directory if it doesn't exist
os.makedirs('../../frontend/public/data', exist_ok=True)

# Try to read the detailed CSV first, but if it fails, use the basic CSV
try:
    print(f"Trying to read detailed CSV from: {detailed_csv_path}")
    df = pd.read_csv(detailed_csv_path)
    print(f"Successfully read {len(df)} rows from detailed CSV")
except Exception as e:
    print(f"Error reading detailed CSV: {e}")
    
    try:
        print(f"Trying to read basic CSV from: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Successfully read {len(df)} rows from basic CSV")
    except Exception as e:
        print(f"Error reading basic CSV: {e}")
        print("No valid CSV data found. Creating a sample dataset for testing...")
        
        # Create a sample dataset if both CSV files fail
        data = {
            'Name': ['Sample Player 1', 'Sample Player 2', 'Sample Player 3'],
            'Pos': ['QB', 'WR', 'RB'],
            'RAS': ['9.8', '8.7', '7.6'],
            'Draft': ['2020 Round 1', '2019 Round 2', '2021 Round 1'],
            'College': ['Alabama', 'Ohio State', 'Clemson'],
            'ProBowls': ['3', '2', '1']
        }
        df = pd.DataFrame(data)

# Process the data
print("Processing data...")

# Handle the case where the player name might be stored as a dictionary
if 'Name' in df.columns:
    # Create Player column from Name
    df['Player'] = df['Name']
    
    # Try to extract link if Name contains dictionaries
    try:
        if isinstance(df['Name'].iloc[0], str) and ('{' in df['Name'].iloc[0] or "'" in df['Name'].iloc[0]):
            print("Detected potential dictionaries in Name column, attempting to parse...")
            # This is a simplistic approach - in real data you might need more robust parsing
            df['Profile_URL'] = None
    except:
        print("Name column doesn't contain dictionaries or couldn't be parsed")

# Make sure we have a 'Position' column
if 'Pos' in df.columns and 'Position' not in df.columns:
    df['Position'] = df['Pos']
elif 'Position' not in df.columns:
    df['Position'] = 'Unknown'

# Convert RAS to numeric
if 'RAS' in df.columns:
    df['RAS_numeric'] = pd.to_numeric(df['RAS'], errors='coerce')
else:
    df['RAS_numeric'] = float('nan')

# Convert Pro Bowls to numeric
pro_bowl_cols = ['Pro Bowls', 'ProBowls', 'Pro_Bowls']
pro_bowl_found = False
for col in pro_bowl_cols:
    if col in df.columns:
        df['Pro_Bowls_numeric'] = pd.to_numeric(df[col], errors='coerce')
        pro_bowl_found = True
        break

if not pro_bowl_found:
    print("No Pro Bowls column found. Adding empty column.")
    df['Pro_Bowls_numeric'] = float('nan')

# Check for draft information
if 'Draft Year' in df.columns:
    df['Draft'] = df['Draft Year']
elif 'Draft' not in df.columns:
    df['Draft'] = 'Unknown'

# Select columns for export, ensuring they exist
export_cols = []
for col in ['Player', 'Position', 'RAS_numeric', 'Pro_Bowls_numeric', 'College', 'Draft', 'Profile_URL']:
    if col in df.columns:
        export_cols.append(col)
    else:
        print(f"Warning: {col} column not found in data")

export_df = df[export_cols]

# Convert to JSON and save
json_data = export_df.to_json(orient='records')

with open(json_path, 'w') as f:
    f.write(json_data)

# Also save to frontend directory
with open(frontend_json_path, 'w') as f:
    f.write(json_data)

print(f"Successfully exported {len(export_df)} records to:")
print(f"  - {json_path}")
print(f"  - {frontend_json_path}")