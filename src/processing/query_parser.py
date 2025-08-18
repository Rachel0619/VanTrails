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
Use your understanding to map similar phrases and concepts to appropriate filters.

Available Filters:
- rating_min/rating_max: 0.0-5.0 (trail ratings)
- difficulty: "Easy", "Intermediate", "Difficult" (case-sensitive, no other values allowed)
- time_min/time_max: hours (0.25-12.0)
- distance_min/distance_max: km (0.5-30.0)
- dog_friendly: true/false (boolean)
- public_transit: true/false (boolean)
- camping: true/false (boolean)

The output dictionary keys should be in this order:
1. rating_min/rating_max
2. difficulty
3. time_min/time_max
4. distance_min/distance_max
5. dog_friendly
6. public_transit
7. camping

Example Query Mappings (not exhaustive):
- "family friendly" → difficulty: "Easy"
- "I want to take my puppy with me" → dog_friendly: true
- "no dogs" → dog_friendly: false
- "accessible by transit" → public_transit: true
- "camping" → camping: true
- "short hike" → time_max: 2.0
- "long hike" → time_max: null (no limit)

IMPORTANT: 
- Return ONLY valid JSON with extracted filters
- Use lowercase "true"/"false" for boolean values (not "True"/"False")
- Round numbers to 1 decimal place (3.0 not 3)
- EXCLUDE any filters that are not specified or cannot be inferred from the query
- Do NOT include null values or unspecified filters in the output
- Keys MUST appear in the exact order specified above
- Format JSON with no spaces after colons

Examples:
Query: "recommend a family friendly, dog friendly trail"
{{"difficulty":"Easy","dog_friendly":true}}

Query: "I want a challenging hike over 5km with great views"
{{"difficulty":"Difficult","distance_min":5.0,"rating_min":4.0}}

Query: "short easy hike accessible by public transit"
{{"difficulty":"Easy","time_max":2.0,"public_transit":true}}

Extract filters from this query: {user_query}
"""
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return text.strip()

    def parse_query_with_llm(self, query: str, llm_function) -> Dict[str, Any]:
        """
        Parse query using LLM to extract filters
        
        Args:
            query: Natural language query
            llm_function: Function that takes prompt and returns LLM response
            
        Returns:
            Dictionary with extracted filters
        """
        user_prompt = self.filter_extraction_prompt + f'"{query}"'
        
        try:
            # Get LLM response
            system_prompt = "You are a query parser. Extract structured filters from natural language queries about hiking trails."
            response = llm_function(user_prompt, system_prompt)
            
            # Clean and parse JSON
            json_text = self._extract_json(response)
            filters_dict = json.loads(json_text)

            # Return dictionary with only non-null values            
            result = {k: v for k, v in filters_dict.items() if v is not None}
            print(f"query_parser result: {result}")

            return result
            
        except Exception as e:
            print(f"parsing failed: {e}")
            return {}  # Return empty dict on failure

