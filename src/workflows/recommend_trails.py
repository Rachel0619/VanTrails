import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag.vector_search import TrailVectorDB
from rag.generate_recommendations import generate_trail_recommendation
from llm.client import llm_function

def recommend_trails(query):
    try:
        if not query:
            yield "Please enter your question"
            return
    
        vector_db = TrailVectorDB(
            host=os.getenv('QDRANT_HOST', 'localhost'),
            port=int(os.getenv('QDRANT_PORT', '6333'))
        )

        search_results = vector_db.search_trails(query, limit=3)
        
        if not search_results:
            yield "I couldn't find any trails matching your criteria. Try a different search."
            return
        
        # Use streaming for recommendation generation
        recommendation_stream = generate_trail_recommendation(query, search_results, llm_function)
        
        # Accumulate the streamed response
        full_response = ""
        for chunk in recommendation_stream:
            full_response += chunk
            yield full_response
    
    except Exception as e:
        print(f"Error in recommend_trails: {e}")
        yield f'Error: {str(e)}'