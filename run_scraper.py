#!/usr/bin/env python3
"""
Vancouver Trails Scraper Runner
Run this script to scrape all trails data from vancouvertrails.com
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.vancouver_trails_scraper import VancouverTrailsScraper

def main():
    print("🏔️  Vancouver Trails Scraper")
    print("=" * 40)
    
    scraper = VancouverTrailsScraper()
    
    try:
        trails = scraper.scrape_all_trails()
        
        if trails:
            scraper.save_to_csv("data/vancouver_trails.csv")
            print(f"\n✅ Successfully scraped {len(trails)} trails!")
            print(f"📄 Data saved to: data/vancouver_trails.csv")
            
            # Show summary statistics
            print(f"\n📊 Summary:")
            print(f"   Total trails: {len(trails)}")
            
            # Count trails with descriptions
            with_desc = sum(1 for t in trails if t.get('description', '').strip())
            print(f"   With descriptions: {with_desc}")
            
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