#!/usr/bin/env python3
"""
Generate personalized trail recommendations using RAG
"""

import sys
import os
from typing import List, Dict, Any, Callable

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from llm.client import llm_function


def generate_trail_recommendation(user_query: str, search_results: list, llm_function: Callable[[str, str], str]) -> str:
    """
    Generate a conversational trail recommendation based on search results
    
    Args:
        user_query: The original user query
        search_results: List of trail results from vector search
        llm_function: Function that takes (system_prompt, user_prompt) and returns response
        
    Returns:
        Natural language recommendation response
    """
    # Handle empty search results
    if not search_results:
        return "Sorry, I can't find any trails that satisfy all the constraints in your request. You might want to try broadening your criteria and try again."
    
    # Format search results for the prompt
    formatted_trails = []
    for i, result in enumerate(search_results, 1):
        trail = result.payload
        score = result.score
        
        trail_info = f"""
Trail {i}: {trail.get('name', 'Unknown')}
- Rating: {trail.get('rating', 'N/A')} stars
- Region: {trail.get('region', 'N/A')}
- Difficulty: {trail.get('difficulty', 'N/A')}
- Time: {trail.get('time', 'N/A')}
- Distance: {trail.get('distance', 'N/A')}
- Season: {trail.get('season', 'N/A')}
- Dog Friendly: {trail.get('dog_friendly', 'N/A')}
- Description: {trail.get('description', 'No description available')}
- Relevance Score: {score:.3f}
        """.strip()
        formatted_trails.append(trail_info)
    
    trails_context = "\n\n".join(formatted_trails)
    
    system_prompt = """You are a knowledgeable Vancouver hiking guide. Based on the user's query and the most relevant trails found, provide a helpful, conversational recommendation.

Guidelines:
- Write in a friendly, informative tone using plain text only (no markdown formatting like ** or ### or -)
- Use natural paragraphs and sentences instead of bullet points or headers
- Highlight the most relevant trails based on the user's specific needs
- Mention key details like difficulty, time, distance, and special features
- Provide practical advice (best seasons, what to bring, parking, etc.)
- If multiple trails are good options, explain the differences to help them choose
- Keep the response comprehensive but not overwhelming (aim for 200-400 words)
- Don't just list trails - provide thoughtful recommendations with reasoning
"""

    user_prompt = f"""User Query: "{user_query}"

Most Relevant Trails Found:
{trails_context}

Please provide a thoughtful recommendation based on the user's query and these trail options."""

    return llm_function(user_prompt, system_prompt, temperature=0.7, max_tokens=600)