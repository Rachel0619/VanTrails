import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Set
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VancouverTrailsScraper:
    def __init__(self, base_url: str = "https://www.vancouvertrails.com"):
        self.base_url = base_url
        self.trails_url = f"{base_url}/trails/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.trails_data = []
        self.existing_trails: Set[str] = set()
        
        # Filter URLs for feature detection
        self.filter_urls = {
            'dog_friendly': f"{base_url}/trails/?filter=dogs",
            'public_transit': f"{base_url}/trails/?filter=transit", 
            'camping': f"{base_url}/trails/?filter=camping"
        }
        

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_trail_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract trail data from the trails list structure."""
        trails = []
        
        # Find the trails list container
        trails_container = soup.find('div', {'id': 'trails-list'})
        if not trails_container:
            logger.error("Could not find trails-list container")
            return trails
        
        trail_list = trails_container.find('ul', class_='traillist')
        if not trail_list:
            logger.error("Could not find traillist ul element")
            return trails
        
        # Find all trail listing items
        trail_items = trail_list.find_all('li', class_='trail-listing')
        logger.info(f"Found {len(trail_items)} trail items")
        
        for item in trail_items:
            trail_data = {}
            
            # Extract trail name and URL
            trail_link = item.find('a')
            if not trail_link:
                continue
                
            trail_data['url'] = urljoin(self.base_url, trail_link.get('href', ''))
            
            # Extract trail name
            trail_name_elem = item.find('span', class_='trailname')
            if trail_name_elem:
                trail_data['name'] = trail_name_elem.get_text(strip=True)
            
            # Extract other trail details from the nested ul
            trail_row = item.find('ul', class_='trail-row')
            if trail_row:
                # Rating
                rating_input = trail_row.find('input', class_='rating')
                if rating_input and rating_input.get('value'):
                    trail_data['rating'] = rating_input.get('value')
                
                # Region
                region_elem = trail_row.find('li', class_='i-name')
                if region_elem:
                    trail_data['region'] = region_elem.get_text(strip=True)
                
                # Difficulty
                difficulty_elem = trail_row.find('li', class_='i-difficulty')
                if difficulty_elem:
                    trail_data['difficulty'] = difficulty_elem.get_text(strip=True)
                
                # Time
                time_elem = trail_row.find('li', class_='i-time')
                if time_elem:
                    trail_data['time'] = time_elem.get_text(strip=True)
                
                # Distance
                distance_elem = trail_row.find('li', class_='i-distance')
                if distance_elem:
                    trail_data['distance'] = distance_elem.get_text(strip=True)
                
                # Season
                season_elem = trail_row.find('li', class_='i-schedule')
                if season_elem:
                    trail_data['season'] = season_elem.get_text(strip=True)
            
            # Only add trails with valid names
            if trail_data.get('name') and trail_data.get('name').strip():
                trails.append(trail_data)
        
        return trails

    def get_trails_with_features(self) -> dict:
        """Get sets of trail names for each feature by scraping filtered pages."""
        feature_trails = {}
        
        for feature, filter_url in self.filter_urls.items():
            logger.info(f"Scraping {feature} trails from {filter_url}")
            soup = self.get_page(filter_url)
            
            if soup:
                trails = self.extract_trail_data(soup)
                trail_names = {trail['name'] for trail in trails if trail.get('name')}
                feature_trails[feature] = trail_names
                logger.info(f"Found {len(trail_names)} trails with {feature}")
                
                # Debug: Show first few trail names for this feature
                sample_trails = list(trail_names)[:3]
                logger.info(f"Sample {feature} trails: {sample_trails}")
                
                # Be respectful to the server
                time.sleep(1)
            else:
                feature_trails[feature] = set()
                logger.warning(f"Failed to load {feature} filter page")
        
        
        return feature_trails

    def extract_trail_description(self, trail_url: str) -> str:
        """Extract detailed description from individual trail page."""
        soup = self.get_page(trail_url)
        if not soup:
            return ""
        
        # Look for the main trail info section
        trail_info = soup.find('div', class_='trail-info')
        if trail_info:
            # Get all paragraphs within trail-info
            paragraphs = trail_info.find_all('p')
            description_parts = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Skip short paragraphs and common elements
                if len(text) > 30 and not any(skip in text.lower() for skip in ['share', 'facebook', 'twitter', 'email']):
                    description_parts.append(text)
            
            if description_parts:
                return ' '.join(description_parts)
        
        # Fallback: look for main content area
        content_area = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if content_area:
            paragraphs = content_area.find_all('p')
            description_parts = []
            
            for p in paragraphs[:5]:  # Take first 5 paragraphs max
                text = p.get_text(strip=True)
                if len(text) > 30:
                    description_parts.append(text)
            
            return ' '.join(description_parts)
        
        return ""

    def load_existing_trails(self, csv_file: str) -> None:
        """Load existing trail names from CSV to avoid re-scraping."""
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                if 'name' in df.columns:
                    self.existing_trails = set(df['name'].dropna())
                    logger.info(f"Loaded {len(self.existing_trails)} existing trails from {csv_file}")
                else:
                    logger.warning(f"No 'name' column found in {csv_file}")
            except Exception as e:
                logger.error(f"Error loading existing trails: {e}")
        else:
            logger.info(f"No existing CSV file found at {csv_file}")

    def scrape_all_trails(self, csv_file: str = "data/vancouver_trails.csv", test_mode: bool = False) -> List[Dict]:
        """Main method to scrape all trail data."""
        logger.info(f"Starting to scrape trails from {self.trails_url}")
        
        # Load existing trails to avoid re-scraping
        self.load_existing_trails(csv_file)
        
        # Get feature data by scraping filtered pages
        print("\n📋 Extracting trail features from filter pages...")
        feature_trails = self.get_trails_with_features()
        
        # Get the main trails page
        soup = self.get_page(self.trails_url)
        if not soup:
            logger.error("Failed to load main trails page")
            return []
        
        # Extract basic trail data from list structure
        all_trails = self.extract_trail_data(soup)
        logger.info(f"Found {len(all_trails)} trails on main page")
        
        # Add accurate feature data to all trails
        for trail in all_trails:
            trail_name = trail.get('name')
            if trail_name:
                # Set features based on filtered page results
                trail['dog_friendly'] = trail_name in feature_trails.get('dog_friendly', set())
                trail['public_transit'] = trail_name in feature_trails.get('public_transit', set())
                trail['camping'] = trail_name in feature_trails.get('camping', set())
                
                # Simple logic: no_dogs_allowed is the opposite of dog_friendly
                trail['no_dogs_allowed'] = not trail['dog_friendly']
        
        # Filter out trails that already exist
        new_trails = [trail for trail in all_trails if trail.get('name') not in self.existing_trails]
        
        if not new_trails:
            print(f"\n✅ No new trails found! All {len(all_trails)} trails already exist in CSV.")
            return []
        
        # Apply test mode limit BEFORE description scraping
        if test_mode:
            original_count = len(new_trails)
            new_trails = new_trails[:10]
            print(f"\n🧪 TEST MODE: Limited to {len(new_trails)} trails (out of {original_count} new trails)")
        else:
            print(f"\n🆕 Found {len(new_trails)} new trails to scrape (skipping {len(all_trails) - len(new_trails)} existing)")
        
        # Enhance each NEW trail with detailed description
        print(f"\n🔄 Scraping detailed descriptions for {len(new_trails)} new trails...")
        for trail in tqdm(new_trails, desc="Extracting descriptions", unit="trail"):
            if trail.get('url'):
                description = self.extract_trail_description(trail['url'])
                trail['description'] = description
                
                # Be respectful to the server
                time.sleep(1)
            else:
                trail['description'] = ""
        
        self.trails_data = new_trails
        return new_trails

    def save_to_csv(self, filename: str = "vancouver_trails.csv") -> None:
        """Save scraped data to CSV file (append new trails to existing)."""
        if not self.trails_data:
            logger.warning("No new data to save")
            return
        
        new_df = pd.DataFrame(self.trails_data)
        
        # Reorder columns for better readability
        column_order = ['name', 'rating', 'region', 'difficulty', 'time', 'distance', 'elevation', 'season', 'dog_friendly', 'no_dogs_allowed', 'public_transit', 'camping', 'url', 'description']
        existing_columns = [col for col in column_order if col in new_df.columns]
        other_columns = [col for col in new_df.columns if col not in column_order]
        new_df = new_df[existing_columns + other_columns]
        
        # If CSV exists, append new data; otherwise create new file
        if os.path.exists(filename):
            try:
                existing_df = pd.read_csv(filename)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_csv(filename, index=False, encoding='utf-8')
                logger.info(f"Appended {len(new_df)} new trails to {filename} (total: {len(combined_df)})")
            except Exception as e:
                logger.error(f"Error appending to CSV: {e}")
                new_df.to_csv(filename, index=False, encoding='utf-8')
                logger.info(f"Saved {len(new_df)} trails to new {filename}")
        else:
            new_df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Saved {len(new_df)} trails to new {filename}")

def main():
    csv_file = "../../data/vancouver_trails.csv"
    scraper = VancouverTrailsScraper()
    trails = scraper.scrape_all_trails(csv_file)
    
    if trails:
        scraper.save_to_csv(csv_file)
        print(f"\n✅ Successfully scraped {len(trails)} new trails!")
        
        # Print sample data
        print("\n🥾 Sample new trail data:")
        for i, trail in enumerate(trails[:3]):
            print(f"\n{i+1}. {trail.get('name', 'Unknown')}")
            print(f"   Rating: {trail.get('rating', 'N/A')}")
            print(f"   Difficulty: {trail.get('difficulty', 'N/A')}")
            print(f"   Distance: {trail.get('distance', 'N/A')}")
            print(f"   Description: {trail.get('description', 'N/A')[:100]}...")
    elif trails == []:
        print("\n✅ All trails already exist in CSV - no new data to scrape!")
    else:
        print("❌ No trails found. Please check the website structure.")

if __name__ == "__main__":
    main()