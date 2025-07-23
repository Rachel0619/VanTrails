#!/usr/bin/env python3
"""
Vancouver Trails Scraper Runner
Run this script to scrape all trails data from vancouvertrails.com
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scrapers.scraper import VancouverTrailsScraper

def main():
    print("🏔️  Vancouver Trails Scraper")
    print("=" * 40)
    
    # Test mode - only scrape 10 trails
    TEST_MODE = False
    
    scraper = VancouverTrailsScraper()
    
    try:
        csv_file = "../../data/vancouver_trails.csv"
        trails = scraper.scrape_all_trails(csv_file, test_mode=TEST_MODE)
        
        if trails:
            scraper.save_to_csv(csv_file)
            print(f"\n✅ Successfully scraped {len(trails)} trails!")
            print(f"📄 Data saved to: {csv_file}")
            
            # Show summary statistics
            print(f"\n📊 Summary:")
            print(f"   Total trails: {len(trails)}")
            
            # Count trails with descriptions
            with_desc = sum(1 for t in trails if t.get('description', '').strip())
            print(f"   With descriptions: {with_desc}")
            
            # Count trails with features
            dog_friendly = sum(1 for t in trails if t.get('dog_friendly'))
            transit = sum(1 for t in trails if t.get('public_transit'))
            camping = sum(1 for t in trails if t.get('camping'))
            print(f"   Dog friendly: {dog_friendly}")
            print(f"   Public transit: {transit}")
            print(f"   Camping: {camping}")
            
            # Show sample
            print(f"\n🥾 Sample trails:")
            for i, trail in enumerate(trails[:3]):
                print(f"   {i+1}. {trail.get('name', 'Unknown')}")
                
        else:
            print("❌ No trails found. Please check the website structure or connection.")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())