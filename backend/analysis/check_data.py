import pandas as pd
import os

def check_measurements_data():
    print("Checking detailed measurements data...")
    
    # Try to load the detailed measurements
    try:
        # Try CSV first as it's easier to inspect
        if os.path.exists('../../backend/data/player_detailed_measurements.csv'):
            df = pd.read_csv('../../backend/data/player_detailed_measurements.csv')
        elif os.path.exists('../../backend/data/player_detailed_measurements.json'):
            df = pd.read_json('../../backend/data/player_detailed_measurements.json')
        else:
            print("No detailed measurements file found")
            return
            
        print(f"Loaded data for {len(df)} players")
        print(f"Columns in the data: {list(df.columns)}")
        
        # Print first few rows to inspect
        print("\nSample data (first 3 rows):")
        print(df.head(3).to_string())
        
        # Check for measurement columns
        measurement_terms = ['height', 'weight', 'bench', 'forty', '40_', '40-yard', 'sprint', 
                            'dash', 'vertical', 'jump', 'broad', 'shuttle', 'cone', 'drill']
        
        potential_measurement_cols = []
        for col in df.columns:
            if any(term in col.lower() for term in measurement_terms):
                potential_measurement_cols.append(col)
        
        print(f"\nFound {len(potential_measurement_cols)} potential measurement columns: {potential_measurement_cols}")
        
        # If no measurement columns, it means the scraper didn't capture them
        if len(potential_measurement_cols) == 0:
            print("\nNo detailed measurements found in the data.")
            print("The scraper likely didn't extract the specific athletic measurements from the player pages.")
            print("Consider updating the scraper to extract these measurements properly.")
        
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    check_measurements_data()