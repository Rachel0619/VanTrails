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

def generate_trail_recommendation(user_query: str, search_results: list, llm_function: Callable):
    """
    Generate a conversational trail recommendation based on search results
    
    Args:
        user_query: The original user query
        search_results: List of trail results from vector search
        llm_function: Function that takes (system_prompt, user_prompt) and returns response
        
    Returns:
        Generator that yields streaming chunks
    """
    # Handle empty search results
    if not search_results:
        yield "Sorry, I can't find any trails that satisfy all the constraints in your request. You might want to try broadening your criteria and try again."
        return
    
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
    
    system_prompt = """You are a knowledgeable Vancouver hiking guide who provides helpful trail recommendations."""

    user_prompt = f"""The user asked: "{user_query}"

I searched our database and found these trails that match their request:

{trails_context}

Please recommend these trails to the user. Guidelines:
- Write in a friendly, informative tone using plain text only (no markdown formatting)
- Use natural paragraphs and sentences instead of bullet points or headers
- Present these as YOUR recommendations to help them with their request
- Explain why each trail is suitable for their specific needs
- Mention key details like difficulty, time, distance, and special features
- Provide practical advice (best seasons, what to bring, parking, etc.)
- Keep the response comprehensive but not overwhelming (aim for 200-400 words)
- Start by directly addressing their request, not commenting on their "plan"
- You can use emojis when necessary to make the response warmer and lighter

Write a recommendation response as if you are suggesting these trails to help with their hiking request."""

    # Get the streaming response from LLM
    stream = llm_function(user_prompt, system_prompt, stream=True)
    
    # Yield each chunk as it comes
    for chunk in stream:
        yield chunk