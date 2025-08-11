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

def llm_function(user_prompt: str, system_prompt: str, temperature: float = 0.1, max_tokens: int = 200) -> str:
    """
    LLM function that can take custom system prompts and generation parameters
    
    Args:
        prompt: The user prompt to send to LLM
        system_prompt: The system prompt (required - no default)
        temperature: Sampling temperature (0.0-2.0, default 0.1 for precise tasks)
        max_tokens: Maximum tokens to generate (default 200 for short responses)
        
    Returns:
        LLM response
    """
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        # temperature=temperature,
        # max_tokens=max_tokens
    )
    
    return response.choices[0].message.content.strip()