import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup, Comment
import time
import os
import re

# Create directories
os.makedirs('../../backend/data/combine_data', exist_ok=True)
os.makedirs('../../frontend/public/data', exist_ok=True)

def scrape_pfr_combine_data(year):
    """Scrape combine data from Pro Football Reference for a specific year"""
    url = f"https://www.pro-football-reference.com/draft/{year}-combine.htm"
    print(f"Scraping combine data from {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Use BeautifulSoup instead of pandas.read_html for more control
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to access URL: {url}. Status code: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pro Football Reference sometimes hides content in comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            if 'table' in comment and 'combine' in comment:
                # Parse the comment as HTML
                comment_soup = BeautifulSoup(comment, 'html.parser')
                # Look for the combine table in the comment
                table = comment_soup.find('table', {'id': 'combine'})
                if table:
                    soup = comment_soup  # Replace soup with the content from the comment
                    break
        
        # Find the combine table
        table = soup.find('table', {'id': 'combine'})
        
        if not table:
            print(f"No combine table found for {year}")
            return None
        
        # Extract headers
        headers_row = table.find('thead').find_all('tr')[-1]  # Get the last header row
        headers = [th.get_text(strip=True) for th in headers_row.find_all(['th', 'td'])]
        
        # Extract data rows
        rows = []
        for row in table.find('tbody').find_all('tr'):
            # Skip header rows that might be in the tbody
            if row.get('class') and 'thead' in row.get('class'):
                continue
                
            # Get all cells
            cells = row.find_all(['th', 'td'])
            row_data = {}
            
            # Get player URL if available
            player_cell = row.find('td', {'data-stat': 'player'})
            if player_cell and player_cell.find('a'):
                row_data['Player_URL'] = "https://www.pro-football-reference.com" + player_cell.find('a')['href']
            else:
                row_data['Player_URL'] = None
            
            # Extract cell values
            for i, cell in enumerate(cells):
                if i < len(headers):
                    # Clean and normalize the header
                    header = headers[i].replace('%', 'Percentile').replace('/', '_')
                    value = cell.get_text(strip=True)
                    row_data[header] = value
            
            rows.append(row_data)
        
        # Create dataframe
        df = pd.DataFrame(rows)
        
        # Clean up the dataframe
        if 'Player' in df.columns:
            df = df.dropna(subset=['Player'])  # Remove rows without player names
        
        # Convert height to inches if available
        if 'Ht' in df.columns:
            df['Height_inches'] = df['Ht'].apply(
                lambda x: int(str(x).split('-')[0]) * 12 + int(str(x).split('-')[1]) if isinstance(x, str) and '-' in str(x) else np.nan
            )
        
        # Add year column
        df['Combine_Year'] = year
        
        print(f"Successfully extracted {len(df)} player records for {year}")
        return df
        
    except Exception as e:
        print(f"Error scraping {year} combine data: {e}")
        return None

def scrape_player_accolades(player_url, max_retries=3):
    """Scrape Pro Bowl and All-Pro information from a player's page"""
    if not player_url:
        return None
    
    accolades = {
        'Pro_Bowl_Count': 0,
        'All_Pro_Count': 0,
        'Pro_Bowl_Years': [],
        'All_Pro_Years': [],
        'Career_AV': None,  # Approximate Value - useful career metric
        'Draft_Pick': None,
        'Draft_Round': None
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Scraping accolades from {player_url}")
            response = requests.get(player_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for Pro Bowls in Awards section
                awards_div = soup.find('div', {'id': 'all_honors'})
                if awards_div:
                    # Pro Football Reference hides content in comments
                    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                        if 'honors' in comment:
                            awards_html = BeautifulSoup(comment, 'html.parser')
                            
                            # Look for Pro Bowl mentions
                            pro_bowl_items = awards_html.find_all('li', string=lambda s: s and 'Pro Bowl' in s)
                            for item in pro_bowl_items:
                                accolades['Pro_Bowl_Count'] += 1
                                # Extract year
                                year_match = re.search(r'(\d{4})', item.text)
                                if year_match:
                                    accolades['Pro_Bowl_Years'].append(year_match.group(1))
                            
                            # Look for All-Pro mentions
                            all_pro_items = awards_html.find_all('li', string=lambda s: s and 'All-Pro' in s)
                            for item in all_pro_items:
                                accolades['All_Pro_Count'] += 1
                                # Extract year
                                year_match = re.search(r'(\d{4})', item.text)
                                if year_match:
                                    accolades['All_Pro_Years'].append(year_match.group(1))
                
                # Get Career Approximate Value
                av_div = soup.find('div', {'id': 'div_stats_ap_career'})
                if av_div:
                    av_row = av_div.find('tr', {'class': 'stat_total'})
                    if av_row:
                        av_cell = av_row.find('td', {'data-stat': 'av'})
                        if av_cell:
                            accolades['Career_AV'] = int(av_cell.text)
                
                # Get draft information
                draft_info = soup.find('div', {'id': 'div_draft_id'})
                if draft_info:
                    draft_row = draft_info.find('tr')
                    if draft_row:
                        # Get draft round
                        round_cell = draft_row.find('td', {'data-stat': 'draft_round'})
                        if round_cell:
                            accolades['Draft_Round'] = round_cell.text
                        
                        # Get draft pick
                        pick_cell = draft_row.find('td', {'data-stat': 'draft_pick'})
                        if pick_cell:
                            pick_text = pick_cell.text.strip()
                            if pick_text and pick_text.isdigit():
                                accolades['Draft_Pick'] = int(pick_text)
                
                return accolades
            
            else:
                print(f"Failed to load {player_url}: HTTP {response.status_code}")
                time.sleep(2)
                
        except Exception as e:
            print(f"Error scraping player accolades from {player_url}: {e}")
            time.sleep(2)
    
    print(f"Failed to get accolades after {max_retries} attempts")
    return accolades

def get_multiple_years_combine_data(years, include_accolades=True, sample_size=None):
    """Get combine data for multiple years and combine into one dataset"""
    all_data = []
    
    for year in years:
        df = scrape_pfr_combine_data(year)
        if df is not None and not df.empty:
            all_data.append(df)
            print(f"Added {len(df)} players from {year}")
    
    if all_data:
        # Combine all years
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Combined dataset has {len(combined_df)} players")
        
        # Limit to sample size if specified (for testing)
        if sample_size and sample_size < len(combined_df):
            combined_df = combined_df.sample(sample_size, random_state=42)
            print(f"Sampled down to {len(combined_df)} players for testing")
        
        # Add Pro Bowl and All-Pro information if requested
        if include_accolades:
            print("Adding Pro Bowl and All-Pro information...")
            
            # Initialize accolade columns
            combined_df['Pro_Bowl_Count'] = 0
            combined_df['All_Pro_Count'] = 0
            combined_df['Career_AV'] = np.nan
            combined_df['Draft_Round'] = None
            combined_df['Draft_Pick'] = np.nan
            
            # Track successful scrapes
            success_count = 0
            
            # Process each player with a URL
            for idx, row in combined_df.iterrows():
                if pd.notna(row.get('Player_URL')):
                    accolades = scrape_player_accolades(row['Player_URL'])
                    if accolades:
                        combined_df.at[idx, 'Pro_Bowl_Count'] = accolades['Pro_Bowl_Count']
                        combined_df.at[idx, 'All_Pro_Count'] = accolades['All_Pro_Count']
                        combined_df.at[idx, 'Career_AV'] = accolades['Career_AV']
                        combined_df.at[idx, 'Draft_Round'] = accolades['Draft_Round']
                        combined_df.at[idx, 'Draft_Pick'] = accolades['Draft_Pick']
                        success_count += 1
                        
                    # Pause to avoid overloading the server
                    time.sleep(1)
                    
                    # Print progress
                    if (idx + 1) % 5 == 0 or idx == len(combined_df) - 1:
                        print(f"Processed {idx + 1}/{len(combined_df)} players ({success_count} successful)")
            
            print(f"Successfully added accolades for {success_count} players")
        
        # Calculate a simplified RAS-like score
        # Convert measurement columns to numeric
        numeric_cols = ['40yd', 'Vertical', 'Broad Jump', '3Cone', 'Shuttle', 'Bench']
        for col in numeric_cols:
            if col in combined_df.columns:
                combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        
        # Calculate score components
        score_components = []
        
        # 40-yard dash (lower is better, so invert)
        if '40yd' in combined_df.columns:
            min_val = combined_df['40yd'].dropna().min()
            max_val = combined_df['40yd'].dropna().max()
            if min_val != max_val:
                combined_df['40yd_score'] = 10 - ((combined_df['40yd'] - min_val) / (max_val - min_val) * 10)
                score_components.append('40yd_score')
        
        # Vertical jump (higher is better)
        if 'Vertical' in combined_df.columns:
            min_val = combined_df['Vertical'].dropna().min()
            max_val = combined_df['Vertical'].dropna().max()
            if min_val != max_val:
                combined_df['Vertical_score'] = ((combined_df['Vertical'] - min_val) / (max_val - min_val) * 10)
                score_components.append('Vertical_score')
        
        # Broad jump (higher is better)
        if 'Broad Jump' in combined_df.columns:
            min_val = combined_df['Broad Jump'].dropna().min()
            max_val = combined_df['Broad Jump'].dropna().max()
            if min_val != max_val:
                combined_df['Broad_score'] = ((combined_df['Broad Jump'] - min_val) / (max_val - min_val) * 10)
                score_components.append('Broad_score')
        
        # 3-cone (lower is better, so invert)
        if '3Cone' in combined_df.columns:
            min_val = combined_df['3Cone'].dropna().min()
            max_val = combined_df['3Cone'].dropna().max()
            if min_val != max_val:
                combined_df['3Cone_score'] = 10 - ((combined_df['3Cone'] - min_val) / (max_val - min_val) * 10)
                score_components.append('3Cone_score')
        
        # Calculate the average score if we have components
        if score_components:
            print(f"Calculating athletic score using {len(score_components)} components: {score_components}")
            combined_df['Athletic_Score'] = combined_df[score_components].mean(axis=1)
            combined_df['Athletic_Score'] = combined_df['Athletic_Score'].round(2)
        
        # Save data
        csv_path = '../../backend/data/combine_data/nfl_combine_data.csv'
        json_path = '../../frontend/public/data/nfl_combine_data.json'
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        combined_df.to_csv(csv_path, index=False)
        combined_df.to_json(json_path, orient='records')
        
        print(f"Data saved successfully to {csv_path} and {json_path}")
        return combined_df
    else:
        print("No data collected")
        return None

if __name__ == "__main__":
    # Scrape data from year 2000
    years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001, 2000]
    
    # For testing, use a small sample
    sample_size = None  # Set to None for all players
    
    combine_df = get_multiple_years_combine_data(years, include_accolades=True, sample_size=sample_size)