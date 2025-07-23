#!/usr/bin/env python3
"""
Query Parser for Vancouver Trails RAG System
Extracts structured filters from natural language queries using LLM
"""

import json
import re
import sys
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add parent directory to path to import llm client
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm.client import llm_function


@dataclass
class TrailFilters:
    """Structured filters for trail search"""
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    difficulty: Optional[str] = None  # Easy, Intermediate, Difficult
    time_min: Optional[float] = None  # hours
    time_max: Optional[float] = None  # hours
    distance_min: Optional[float] = None  # km
    distance_max: Optional[float] = None  # km
    region: Optional[str] = None
    season: Optional[str] = None
    dog_friendly: Optional[bool] = None
    public_transit: Optional[bool] = None
    camping: Optional[bool] = None

class QueryParser:
    """Extract structured filters from natural language queries"""
    
    def __init__(self):
        self.filter_extraction_prompt = self._build_prompt()
    
    def _build_prompt(self) -> str:
        """Build the LLM prompt for filter extraction"""
        return """You are a hiking trail query parser. Extract structured filters from user queries about Vancouver hiking trails.

Available Filters:
- rating_min/rating_max: 0.0-5.0 (trail ratings)
- difficulty: "Easy", "Intermediate", "Difficult" 
- time_min/time_max: hours (0.25-12.0)
- distance_min/distance_max: km (0.5-30.0)
- region: "Fraser Valley East", "Tri Cities", "Howe Sound", "North Shore", "Sea To Sky", etc.
- season: "year-round", "May - October", "July - October", etc.
- dog_friendly: true/false
- public_transit: true/false  
- camping: true/false

Example Query Mappings (not exhaustive):
- "family friendly" → difficulty: "Easy"
- "dog friendly" → dog_friendly: true
- "no dogs" → dog_friendly: false
- "accessible by transit" → public_transit: true
- "camping" → camping: true
- "short hike" → time_max: 2.0
- "long hike" → time_max: null (no limit)
- "close to vancouver" → region: "North Shore" or "Tri Cities"

Use your understanding to map similar phrases and concepts to appropriate filters.

Return ONLY valid JSON with extracted filters. Use null for unspecified filters.

Examples:
Query: "recommend a family friendly, dog friendly trail"
{"difficulty": "Easy", "dog_friendly": true}

Query: "I want a challenging hike over 5km with great views"
{"difficulty": "Difficult", "distance_min": 5.0, "rating_min": 4.0}

Query: "short easy hike accessible by public transit"
{"difficulty": "Easy", "time_max": 2.0, "public_transit": true}

Extract filters from this query:
"""

    def parse_query_with_llm(self, query: str, llm_function) -> TrailFilters:
        """
        Parse query using LLM to extract filters
        
        Args:
            query: Natural language query
            llm_function: Function that takes prompt and returns LLM response
            
        Returns:
            TrailFilters object with extracted filters
        """
        full_prompt = self.filter_extraction_prompt + f'"{query}"'
        
        try:
            # Get LLM response
            response = llm_function(full_prompt)
            
            # Clean and parse JSON
            json_text = self._extract_json(response)
            filters_dict = json.loads(json_text)
            
            # Convert to TrailFilters object
            return TrailFilters(**{k: v for k, v in filters_dict.items() if v is not None})
            
        except Exception as e:
            print(f"⚠️  LLM parsing failed: {e}")
            return TrailFilters()  # Return empty filters on failure
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return text.strip()
    

    def filters_to_dict(self, filters: TrailFilters) -> Dict[str, Any]:
        """Convert TrailFilters to dictionary for DataFrame filtering"""
        return {k: v for k, v in filters.__dict__.items() if v is not None}


