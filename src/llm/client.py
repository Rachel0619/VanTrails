#!/usr/bin/env python3
"""
Simple LLM client for query parsing
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_function(prompt: str) -> str:
    """
    Simple LLM function for query parser
    
    Args:
        prompt: The prompt to send to LLM
        
    Returns:
        LLM response
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise filter extraction system. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip()