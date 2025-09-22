#!/usr/bin/env python3
"""
Qdrant Vector Database Setup for Vancouver Trails
Ingests trail data with Jina embeddings and metadata
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import pandas as pd
import hashlib
from typing import List, Dict, Any
from qdrant_client import QdrantClient, models
from tqdm import tqdm
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from processing.query_parser import QueryParser
from llm.client import llm_function
# Tracing imports removed for now

load_dotenv()

# Configuration
EMBEDDING_DIMENSIONALITY = os.getenv('EMBEDDING_DIMENSIONALITY')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
QDRANT_HOST = os.getenv('QDRANT_HOST')
QDRANT_PORT = int(os.getenv('QDRANT_PORT'))
MODEL_NAME = os.getenv('MODEL_NAME')

class TrailVectorDB:
    """Qdrant vector database for trails"""
    
    def __init__(self, host: str = QDRANT_HOST, port: int = QDRANT_PORT):
        """Initialize Qdrant client and embedding model"""
        self.client = QdrantClient(host=host, port=port)   
    
    def create_collection(self):
        """Create collection if it doesn't exist"""
        print(f"Checking collection: {COLLECTION_NAME}")
        
        # Check if collection exists
        try:
            collection_info = self.client.get_collection(COLLECTION_NAME)
            print(f"   Collection exists with {collection_info.points_count} points")
            return False  # Collection already exists
        except:
            # Collection doesn't exist, create it
            print("   Creating new collection...")
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIMENSIONALITY,
                    distance=models.Distance.COSINE
                )
            )
            print("Collection created successfully")
            return True  # New collection created
    
    def get_existing_trails(self) -> set:
        """Get existing trail identifiers (name_url) from the collection"""
        try:
            # Scroll through all points to get trail names and URLs
            points, _ = self.client.scroll(
                collection_name=COLLECTION_NAME,
                limit=1000,  # Get all points
                with_payload=True
            )
            
            existing_trails = set()
            for point in points:
                if 'name' in point.payload and 'url' in point.payload:
                    trail_key = f"{point.payload['name']}_{point.payload['url']}"
                    existing_trails.add(trail_key)
            
            return existing_trails
        except Exception as e:
            print(f"   Warning: Could not check existing points: {e}")
            return set()
    
    def prepare_new_trail_data(self, csv_path: str) -> List[models.PointStruct]:
        """Load and prepare only new trail data for Qdrant"""
        print(f"📄 Loading trail data from {csv_path}")
        
        # Load trails data
        df = pd.read_csv(csv_path)
        print(f"   Found {len(df)} trails")
        
        # Check which trails already exist (by name_url)
        print("   Checking for existing trails...")
        existing_trails = self.get_existing_trails()
        print(f"   Found {len(existing_trails)} existing trails")
        
        # Prepare only new points
        new_points = []
        for _, row in df.iterrows():
            # Create trail identifier
            trail_key = f"{row['name']}_{row['url']}"
            
            # Skip if trail already exists
            if trail_key in existing_trails:
                continue
            
            # Text for embedding (description)
            description = str(row['description']) if pd.notna(row['description']) else ""
            
            # Create vector using Qdrant's text embedding
            vector = models.Document(text=description, model=MODEL_NAME)
            
            # Prepare metadata
            payload = {
                'name': str(row['name']),
                'rating': float(row['rating']) if pd.notna(row['rating']) else 0.0,
                'region': str(row['region']),
                'difficulty': str(row['difficulty']),
                'time': float(row['time']) if pd.notna(row['time']) else 0.0,
                'distance': float(row['distance']) if pd.notna(row['distance']) else 0.0,
                'season': str(row['season']),
                'dog_friendly': bool(row['dog_friendly']),
                'no_dogs_allowed': bool(row['no_dogs_allowed']),
                'public_transit': bool(row['public_transit']),
                'camping': bool(row['camping']),
                'url': str(row['url']),
                'description': description
            }
            
            # Create point with unique ID (hash of trail_key)
            point = models.PointStruct(
                id=hash(trail_key) & 0x7FFFFFFF,  # Ensure positive 32-bit integer
                vector=vector,
                payload=payload
            )
            new_points.append(point)
        
        print(f"   {len(new_points)} new trails to ingest")
        return new_points
    
    def ingest_trails(self, csv_path: str):
        """Complete ingestion process - only new trails"""
        print("Starting incremental trail ingestion")
        print("=" * 50)
        
        # Prepare only new data
        new_points = self.prepare_new_trail_data(csv_path)
        
        if not new_points:
            print("No new trails to ingest - database is up to date!")
            collection_info = self.client.get_collection(COLLECTION_NAME)
            return collection_info.points_count
        
        # Upload new points to Qdrant
        print(f"Uploading {len(new_points)} new trails...")
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=new_points
        )
        
        # Verify ingestion
        collection_info = self.client.get_collection(COLLECTION_NAME)
        print(f"Total trails in database: {collection_info.points_count}")
        print(f"   ({len(new_points)} newly added)")
        
        return collection_info.points_count
    
    def build_qdrant_filter(self, filters_dict: Dict):
        """Convert filters to Qdrant format"""

        conditions = []
        
        for key, value in filters_dict.items():
            if key.endswith('_min'):
                field = key[:-4]  # Remove '_min'
                conditions.append(models.FieldCondition(key=field, range=models.Range(gte=value)))
            elif key.endswith('_max'):
                field = key[:-4]  # Remove '_max'
                conditions.append(models.FieldCondition(key=field, range=models.Range(lte=value)))
            else:
                conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=value)))
        
        return models.Filter(must=conditions) if conditions else None
    
    def search_trails(self, query: str, limit: int = 3):
        """Search trails by semantic similarity"""
        # Prepare Qdrant filters
        query_parser = QueryParser()
        filters_dict = query_parser.parse_query_with_llm(query, llm_function)
        qdrant_filter = self.build_qdrant_filter(filters_dict)
        
        # Search using query_points
        query_points = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=models.Document(
                text=query,
                model=MODEL_NAME
            ),
            query_filter=qdrant_filter,
            limit=limit,
            with_payload=True
        )
        
        # Extract results
        results = []
        for point in query_points.points:
            results.append(point)
        
        return results


