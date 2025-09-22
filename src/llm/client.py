#!/usr/bin/env python3
"""
Simple LLM client for query parsing
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Tracing imports removed for now

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Note: GPT-5-mini is fixed-temperature model that only runs at temperature=1
def llm_function(user_prompt: str, system_prompt: str, stream: bool = False):
    """
    LLM function that can take custom system prompts and generation parameters
    
    Args:
        prompt: The user prompt to send to LLM
        system_pdurompt: The system prompt (required - no default)
        temperature: Sampling temperature (0.0-2.0, default 0.1 for precise tasks)
        max_tokens: Maximum tokens to generate (default 200 for short responses)
        stream: Whether to stream the response (default False)
        
    Returns:
        LLM response (string if not streaming, generator if streaming)
    """
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=stream
    )
    
    if stream:
        # Return generator for streaming
        def stream_generator():
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        return stream_generator()
    else:
        # Return complete response for non-streaming
        return response.choices[0].message.content.strip()