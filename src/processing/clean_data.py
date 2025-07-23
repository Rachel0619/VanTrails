#!/usr/bin/env python3
"""
Data Cleaning Script for Vancouver Trails
Cleans the raw scraped data for use in the RAG application
"""

import pandas as pd
import re

def clean_vancouver_trails_data(input_file: str = "../../data/vancouver_trails.csv", 
                               output_file: str = "../../data/vancouver_trails_clean.csv"):
    """
    Clean the Vancouver trails dataset.
    
    Transformations:
    1. Round rating to 1 decimal place
    2. Convert time from "X hours" to float hours
    3. Convert distance from "Xkm" to float km
    """
    
    print("🧹 Cleaning Data")
    print("=" * 40)
    
    # Load the data
    df = pd.read_csv(input_file)
    print(f"📊 Loaded {len(df)} trails")
    
    # 1. Round rating to 1 decimal place
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating'] = df['rating'].round(1)
    print("✅ Rounded ratings to 1 decimal place")
    
    # 2. Clean time column - extract hours and convert to float
    def clean_time(time_str):
        if pd.isna(time_str):
            return None
        
        # Convert to string
        time_str = str(time_str).lower()
        
        # Handle ranges like "1.5 - 2 hours" - take the first number
        if '-' in time_str:
            time_str = time_str.split('-')[0].strip()
        
        # Extract first number from strings like "1.5 hours", "3 hours", "1 hour"
        match = re.search(r'(\d+\.?\d*)', time_str)
        if match:
            return float(match.group(1))
        
        return None
    
    df['time'] = df['time'].apply(clean_time)
    print("✅ Converted time to hours (numeric)")
    
    # 3. Clean distance column - extract km and convert to float
    def clean_distance(distance_str):
        if pd.isna(distance_str):
            return None
            
        # Convert to string
        distance_str = str(distance_str).lower()
        
        # Extract first number from strings like "4km", "7.5km"
        match = re.search(r'(\d+\.?\d*)', distance_str)
        if match:
            return float(match.group(1))
        
        return None
    
    df['distance'] = df['distance'].apply(clean_distance)
    print("✅ Converted distance to km (numeric)")
    
    # Show cleaning results
    print(f"\n📈 Cleaning Results:")
    print(f"   Rating range: {df['rating'].min():.1f} - {df['rating'].max():.1f}")
    print(f"   Time range: {df['time'].min():.1f} - {df['time'].max():.1f} hours")
    print(f"   Distance range: {df['distance'].min():.1f} - {df['distance'].max():.1f} km")
    
    # Count missing values
    missing_time = df['time'].isna().sum()
    missing_distance = df['distance'].isna().sum()
    print(f"   Missing time values: {missing_time}")
    print(f"   Missing distance values: {missing_distance}")
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved cleaned data to: {output_file}")
    
    # Show sample of cleaned data
    print(f"\n🎯 Sample cleaned data:")
    sample_cols = ['name', 'rating', 'time', 'distance', 'difficulty']
    print(df[sample_cols].head(3).to_string(index=False))
    
    return df

def main():
    clean_vancouver_trails_data()
    print(f"\n✅ Data cleaning complete! Ready for RAG application.")

if __name__ == "__main__":
    main()