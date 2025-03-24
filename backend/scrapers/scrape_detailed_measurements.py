import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import json
import ast  # For safely evaluating string representations of dictionaries

def scrape_player_measurements():
    print("Starting to scrape detailed player measurements...")
    
    # Create directories if they don't exist
    os.makedirs('../../backend/data', exist_ok=True)
    
    # Load the existing Pro Bowler data
    try:
        df = pd.read_csv('../../backend/data/pro_bowlers_ras.csv')
        print(f"Loaded data for {len(df)} players")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Extract player links
    player_links = []
    
    # Check if the 'Links' column exists and parse the dictionary-like strings
    if 'Links' in df.columns:
        print("Extracting URLs from Links column")
        for link_data in df['Links']:
            try:
                # The link data appears to be a string representation of a dictionary
                if isinstance(link_data, str) and 'link' in link_data:
                    # Try to safely evaluate the string as a dictionary
                    try:
                        link_dict = ast.literal_eval(link_data)
                        if isinstance(link_dict, dict) and 'link' in link_dict:
                            player_links.append(link_dict['link'])
                        else:
                            # Try regex as a fallback
                            match = re.search(r'\'link\'\s*:\s*\'(https?://[^\']+)\'', link_data)
                            if match:
                                player_links.append(match.group(1))
                    except:
                        # Use regex as a fallback
                        match = re.search(r'\'link\'\s*:\s*\'(https?://[^\']+)\'', link_data)
                        if match:
                            player_links.append(match.group(1))
            except Exception as e:
                print(f"Error processing link data: {e}")
    
    # If no links were found, try to construct them from player names
    if not player_links:
        print("No links found in data, attempting to construct URLs from player names")
        base_url = "https://ras.football/?s="
        
        # Column containing player names
        name_col = 'Name' if 'Name' in df.columns else 'Player' if 'Player' in df.columns else None
        
        if name_col:
            for name in df[name_col]:
                if isinstance(name, str):
                    # Format name for URL (replace spaces with +)
                    formatted_name = name.replace(' ', '+')
                    player_links.append(f"{base_url}{formatted_name}")
    
    print(f"Found {len(player_links)} player links to process")
    
    if len(player_links) > 0:
        # Sample a few links for testing
        sample_size = min(5, len(player_links))
        print(f"Sample of {sample_size} links:")
        for i in range(sample_size):
            print(f"  {player_links[i]}")
    else:
        print("No valid links found. Exiting.")
        return
    
    # Function to extract player ID from URL
    def extract_player_id(url):
        match = re.search(r'PlayerID=(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    # Function to scrape detailed measurements from a player's page
    def scrape_player_page(url, player_name=None):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # If it's a search URL, we need to find the player's profile page first
            if '?s=' in url:
                print(f"Searching for player: {player_name}")
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Error accessing search page: {response.status_code}")
                    return None
                
                # Parse the search results
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for search results that might contain player links
                search_results = soup.find_all('h2', {'class': 'entry-title'})
                
                if not search_results:
                    print("No search results found")
                    return None
                
                # Find the first result that matches the player name
                player_link = None
                for result in search_results:
                    link = result.find('a')
                    if link and player_name and player_name.lower() in link.text.lower():
                        player_link = link['href']
                        break
                
                if not player_link:
                    print("Could not find player's profile link in search results")
                    return None
                
                # Now access the player's profile page
                url = player_link
                response = requests.get(url, headers=headers)
            else:
                # Directly access the profile page
                response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error accessing player page: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract player name from page
            player_name_elem = soup.find('h1', {'class': 'entry-title'})
            if player_name_elem:
                player_name = player_name_elem.text.strip()
            
            # Extract RAS score
            ras_score_elem = soup.find('div', {'class': 'ras-score-big'})
            ras_score = ras_score_elem.text.strip() if ras_score_elem else None
            
            # Extract all measurements
            measurements = {}
            
            # Find all measurement elements
            measurement_divs = soup.find_all('div', {'class': 'measurement'})
            
            for div in measurement_divs:
                label_elem = div.find('div', {'class': 'label'})
                value_elem = div.find('div', {'class': 'value'})
                
                if label_elem and value_elem:
                    label = label_elem.text.strip()
                    value = value_elem.text.strip()
                    
                    # Convert to a safe column name
                    safe_label = label.replace(' ', '_').replace('-', '_').lower()
                    measurements[safe_label] = value
            
            # Add extra data
            measurements['player_name'] = player_name
            measurements['ras_score'] = ras_score
            measurements['profile_url'] = url
            
            # Extract player ID if available
            player_id = extract_player_id(url)
            if player_id:
                measurements['player_id'] = player_id
            
            return measurements
            
        except Exception as e:
            print(f"Error scraping player page: {e}")
            return None
    
    # Prepare to store all measurements
    all_measurements = []
    
    # Number of players to process (set to a smaller number for testing)
    # Comment this out to process all players
    # player_links = player_links[:20]
    
    # Process each player
    for i, link in enumerate(player_links):
        print(f"Processing player {i+1}/{len(player_links)}: {link}")
        
        # Get player name for search URLs
        name_col = 'Name' if 'Name' in df.columns else 'Player' if 'Player' in df.columns else None
        player_name = df.iloc[i][name_col] if name_col and i < len(df) else None
        
        # Scrape the player's page
        measurements = scrape_player_page(link, player_name)
        
        if measurements:
            # Add position if available
            pos_col = 'Pos' if 'Pos' in df.columns else 'Position' if 'Position' in df.columns else None
            if pos_col and i < len(df):
                measurements['position'] = df.iloc[i][pos_col]
            
            # Add Pro Bowl count if available
            pb_col = 'ProBowls' if 'ProBowls' in df.columns else 'Pro Bowls' if 'Pro Bowls' in df.columns else None
            if pb_col and i < len(df):
                measurements['pro_bowls'] = df.iloc[i][pb_col]
            
            all_measurements.append(measurements)
            print(f"Successfully scraped data for {measurements.get('player_name', 'unknown player')}")
        
        # Pause between requests to avoid overwhelming the server
        time.sleep(2)
    
    # Convert to DataFrame
    if all_measurements:
        measurements_df = pd.DataFrame(all_measurements)
        
        # Save as CSV
        measurements_df.to_csv('../../backend/data/player_detailed_measurements.csv', index=False)
        
        # Also save as JSON for easier processing
        measurements_df.to_json('../../backend/data/player_detailed_measurements.json', orient='records')
        
        print(f"Saved detailed measurements for {len(measurements_df)} players")
        print(f"Measurements included: {list(measurements_df.columns)}")
    else:
        print("No measurements were collected")

if __name__ == "__main__":
    scrape_player_measurements()