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
        csv_path = "data/vancouver_trails_clean.csv"
        final_count = vector_db.ingest_trails(csv_path)
        
        print(f"\n🎯 Vector database ingestion complete!")
        print(f"   Total trails: {final_count}")
            
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return 1
    
    return 0