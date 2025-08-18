from flask import Blueprint, request, jsonify, current_app, g
import sys
import os
import uuid

# import RAG components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag.vector_search import TrailVectorDB
from rag.generate_recommendations import generate_trail_recommendation
from llm.client import llm_function

bp = Blueprint('api', __name__, url_prefix='/api')


def get_vector_db():
    """Get vector database connection, creating it if it doesn't exist"""
    if 'vector_db' not in g:
        g.vector_db = TrailVectorDB(
            host=current_app.config['QDRANT_HOST'],
            port=current_app.config['QDRANT_PORT']
        )
    return g.vector_db


def init_app(app):
    """Initialize services with the Flask app"""
    # Test connections on startup
    with app.app_context():
        try:
            # Test vector database connection
            vector_db = TrailVectorDB(
                host=app.config['QDRANT_HOST'],
                port=app.config['QDRANT_PORT']
            )
            print(f"Connected to Qdrant at {app.config['QDRANT_HOST']}:{app.config['QDRANT_PORT']}")
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            
        # Test LLM configuration
        if app.config.get('OPENAI_API_KEY'):
            print("OpenAI API key configured")
        else:
            print("OpenAI API key not found - set OPENAI_API_KEY environment variable")


@bp.route('/recommend', methods=['POST'])
def recommend_trails():
    """
    Request: {"query": "I want an easy hike with my dog"}
    Response: {"recommendation": "AI generated response..."}
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Please provide a query'}), 400
            
        query = data['query']

        conversation_id = str(uuid.uuid4())
    
        vector_db = get_vector_db()
        search_results = vector_db.search_trails(query, limit=5)
        
        if not search_results:
            return jsonify({
                'query': query,
                'recommendation': "I couldn't find any trails matching your criteria. Try a different search."
            })
        
        # Get the streaming recommendation and collect all chunks
        print(f"About to call generate_trail_recommendation with {len(search_results)} results")
        recommendation_stream = generate_trail_recommendation(query, search_results, llm_function)
        print(f"Got recommendation_stream: {type(recommendation_stream)}")
        
        chunks = []
        for chunk in recommendation_stream:
            print(f"Got chunk: {repr(chunk)}")
            chunks.append(chunk)
        
        recommendation = "".join(chunks)
        print(f"Final recommendation length: {len(recommendation)}")
        
        result = {
            "conversation_id": conversation_id,
            'query': query,
            'recommendation': recommendation
        }

        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from vantrails import create_app
    
    app = create_app()
    
    print("Starting VanTrails API...")
    print("Health check: http://localhost:8000/health")
    print("Trail recommendations: POST http://localhost:8000/api/recommend")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
