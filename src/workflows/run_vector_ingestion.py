#!/usr/bin/env python3
"""
Vector Database Ingestion Workflow
Executes trail data ingestion into Qdrant
"""

import os
import sys

# Suppress HuggingFace warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag.vector_search import TrailVectorDB
from processing.query_parser import QueryParser
from llm.client import llm_function


def main():
    """Run vector database ingestion workflow"""
    try:
        print("🏔️  Vector Database Ingestion Workflow")
        print("=" * 50)
        
        # Initialize vector database
        vector_db = TrailVectorDB()
        
        # Create collection (handles existence check internally)
        is_new_collection = vector_db.create_collection()
        
        # Ingest trail data (handles incremental ingestion internally)
        csv_path = "../../data/vancouver_trails_clean.csv"
        final_count = vector_db.ingest_trails(csv_path)
        
        print(f"\n🎯 Vector database ingestion complete!")
        print(f"   Total trails: {final_count}")
        
        # Test search functionality for new collections
        if is_new_collection:
            test_search(vector_db)
            
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return 1
    
    return 0


def test_search(vector_db):
    """Test search functionality with sample query"""
    print(f"\n🔍 Testing Search Functionality")
    print("=" * 50)
    
    # Test query
    test_query = "beginner hike under 2 hours near water or waterfalls"
    print(f"Query: '{test_query}'")
    
    try:
        # Extract filters using query parser
        query_parser = QueryParser()
        filters = query_parser.parse_query_with_llm(test_query, llm_function)
        filters_dict = query_parser.filters_to_dict(filters)
        
        print(f"🎯 Extracted filters: {filters_dict}")
        
        # Search with filters
        results = vector_db.search_trails(test_query, filters_dict, limit=3)
        
        print(f"\n🏔️  Found {len(results)} trails:")
        for i, result in enumerate(results, 1):
            trail = result.payload
            score = result.score
            print(f"\n{i}. **{trail['name']}** (Score: {score:.3f})")
            print(f"   📍 {trail['region']} | ⏱️  {trail['time']:.1f}h | 📏 {trail['distance']:.1f}km | 🥾 {trail['difficulty']}")
            print(f"   🔗 {trail['url']}")
            
    except Exception as e:
        print(f"⚠️  Search test failed: {e}")


if __name__ == "__main__":
    exit(main())