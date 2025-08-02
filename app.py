import gradio as gr
# import RAG components
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.vector_search import TrailVectorDB
from rag.generate_recommendations import generate_trail_recommendation
from llm.client import llm_function

def recommend_trails(query):
    try:
        if not query:
            return "Please enter your question"
    
        vector_db = TrailVectorDB(
            host=os.getenv('QDRANT_HOST', 'localhost'),
            port=int(os.getenv('QDRANT_PORT', '6333'))
        )
        search_results = vector_db.search_trails(query, limit=5)
        
        if not search_results:
            return "I couldn't find any trails matching your criteria. Try a different search."
        
        recommendation = generate_trail_recommendation(query, search_results, llm_function)

        return recommendation
    
    except Exception as e:
        return f'Error: {str(e)}'

demo = gr.Interface(
    fn=recommend_trails,
    inputs=[gr.Textbox(label="question")],
    outputs=[gr.Textbox(label="recommendation")],
)

demo.launch(server_name="0.0.0.0", server_port=7860)