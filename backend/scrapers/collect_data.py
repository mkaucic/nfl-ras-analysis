import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

# Make sure the data directory exists
os.makedirs('../../backend/data', exist_ok=True)

def scrape_pro_bowler_ras():
    url = "https://ras.football/pro-bowlers-and-ras/"
    
    # Add user-agent header to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Sending request to {url}...")
    response = requests.get(url, headers=headers)
    
    print(f"Response status code: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to fetch the page. Status code:", response.status_code)
        return None
    
    # Save HTML for debugging
    with open("response.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved response HTML to 'response.html' for debugging")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try different table selectors
    print("Looking for table...")
    table = soup.find('table', {'class': 'tablepress'})
    
    if not table:
        print("Tablepress class not found, trying other selectors...")
        table = soup.find('table')  # Try any table
    
    if not table:
        print("No table found. Checking for possible data containers...")
        
        # Look for div elements that might contain the data
        data_divs = soup.find_all('div', {'class': lambda c: c and 'data' in c.lower()})
        if data_divs:
            print(f"Found {len(data_divs)} potential data container divs")
        
        return None
    
    print(f"Table found with {len(table.find_all('tr'))} rows")
    
    # Extract header
    headers = []
    thead = table.find('thead')
    if thead:
        for th in thead.find_all('th'):
            headers.append(th.text.strip())
        print(f"Found table headers: {headers}")
    else:
        print("No thead found, looking for header row...")
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.text.strip())
            print(f"Found headers from first row: {headers}")
    
    # Extract rows
    rows = []
    tbody = table.find('tbody')
    row_elements = tbody.find_all('tr') if tbody else table.find_all('tr')[1:] if table.find_all('tr') else []
    
    print(f"Processing {len(row_elements)} data rows...")
    
    for tr in row_elements:
        row = []
        for td in tr.find_all('td'):
            # Check if there's a link to the player's RAS profile
            link = td.find('a')
            if link and 'href' in link.attrs:
                # Store both the text and the link
                row.append({
                    'text': td.text.strip(),
                    'link': link['href']
                })
            else:
                row.append(td.text.strip())
        if row:  # Only add non-empty rows
            rows.append(row)
    
    print(f"Extracted {len(rows)} data rows")
    
    if not rows:
        print("No data rows found. Table structure might be different.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # If we have header columns, rename the DataFrame columns
    if headers and len(headers) == df.shape[1]:
        df.columns = headers
        print("Applied headers to DataFrame")
    else:
        print(f"Header count ({len(headers) if headers else 0}) doesn't match column count ({df.shape[1]})")
    
    return df


def get_detailed_ras_data(profile_url):
    """Scrape detailed RAS data from a player's profile page"""
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract detailed metrics
    player_data = {}
    
    # Basic info
    player_name_elem = soup.find('h1', {'class': 'entry-title'})
    if player_name_elem:
        player_data['name'] = player_name_elem.text.strip()
    else:
        player_data['name'] = "Unknown Player"
    
    # Find RAS score
    ras_div = soup.find('div', {'class': 'ras-score-big'})
    if ras_div:
        player_data['ras_score'] = ras_div.text.strip()
    
    # Get measurement data
    measurements = {}
    measurement_divs = soup.find_all('div', {'class': 'measurement'})
    for div in measurement_divs:
        label = div.find('div', {'class': 'label'})
        value = div.find('div', {'class': 'value'})
        if label and value:
            measurements[label.text.strip()] = value.text.strip()
    
    player_data['measurements'] = measurements
    
    return player_data

# For each player in our dataset, fetch their detailed profile
def enrich_pro_bowler_data(df):
    detailed_data = []
    
    for index, row in df.iterrows():
        # Check if there's a link to follow - use 'Name' instead of 'Player'
        if isinstance(row['Name'], dict) and 'link' in row['Name']:
            profile_url = row['Name']['link']
            print(f"Fetching data for {row['Name']['text']} ({index+1}/{len(df)})")
            
            # Avoid overwhelming the server
            time.sleep(1)
            
            # Get detailed data
            player_details = get_detailed_ras_data(profile_url)
            
            # Combine with original row data
            combined_data = {
                'Player': row['Name']['text'],
                'Profile_URL': profile_url,
                'Position': row['Pos'] if 'Pos' in row else None,
                'Draft': row['Draft Year'] if 'Draft Year' in row else None,
                'College': row['College'] if 'College' in row else None,
                'Pro_Bowls': row['ProBowls'] if 'ProBowls' in row else None,
                'RAS': row['RAS'] if 'RAS' in row else None
            }
            
            # Add the detailed measurements
            if 'measurements' in player_details:
                for k, v in player_details['measurements'].items():
                    combined_data[k.replace(' ', '_')] = v
            
            detailed_data.append(combined_data)
    
    return pd.DataFrame(detailed_data)

if __name__ == "__main__":
    print("Starting Pro Bowler RAS data collection...")
    
    # Run the scraper for basic data
    pro_bowlers_df = scrape_pro_bowler_ras()
    
    if pro_bowlers_df is not None:
        # Save basic data
        pro_bowlers_df.to_csv('../../backend/data/pro_bowlers_ras.csv', index=False)
        print(f"Saved basic data for {len(pro_bowlers_df)} Pro Bowlers")
        
        # Enrich with detailed player data
        print("Collecting detailed player data (this may take a while)...")
        enriched_df = enrich_pro_bowler_data(pro_bowlers_df)
        
        # Save enriched data
        enriched_df.to_csv('../../backend/data/pro_bowlers_ras_detailed.csv', index=False)
        print(f"Saved detailed data for {len(enriched_df)} Pro Bowlers")
        
        # Save a JSON version for the frontend
        enriched_df.to_json('../../backend/data/pro_bowlers_ras.json', orient='records')
        print(f"Saved JSON data for frontend use")
        
        print("Data collection complete!")
    else:
        print("Data collection failed.")