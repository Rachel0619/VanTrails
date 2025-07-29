# VanTrails

An intelligent RAG application that provides personalized Vancouver hiking trail recommendations.

![VanTrails Cover](images/cover.jpg)

## Project Overview

Finding the right hiking trail in Vancouver can be overwhelming with thousands of available options. Generic search results often miss the nuances of what makes a trail perfect for your specific needs while reading and researching comments from other hikers on social media is very time consuming.

VanTrails is an intelligent trail recommendation system that helps hikers discover the perfect trails in Vancouver, BC. Using advanced RAG technology, the system provides personalized, conversational recommendations based on user queries like "I want an easy hike with my dog near Vancouver" or "Show me challenging winter trails with great views."

## Dataset

The system is powered by a comprehensive dataset of Vancouver-area trails including:

- **Coverage**: 200+ trails across Metro Vancouver, Fraser Valley, Howe Sound, and surrounding regions
- **Trail Information**:
  - Name, rating, and region
  - Difficulty level and estimated time
  - Distance and elevation details
  - Seasonal accessibility
  - Dog-friendly status and restrictions
  - Public transit accessibility
  - Camping availability
  - Detailed descriptions with practical tips

## Technologies

- Python 3.13: Modern Python with latest features
- Qdrant: High-performance vector database for semantic search
- OpenAI GPT-4o-mini: Language model for generating recommendations

## Getting Started

### Prerequisites
- Python 3.13+
- UV package manager
- Qdrant server (local or cloud)
- OpenAI API key (or other LLM provider)

### Preparation

- uv
- OpenAI API

### Using the application

```bash
uv run answer.py
```

```bash
URL=http://localhost:8000
QUERY="I want an easy hike with my dog which is less than 5 km for total distance"
DATA='{
    "query": "'${QUERY}'"
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${DATA}" \
    ${URL}/api/recommend
```

## Key Features

- Semantic Search: Understands natural language queries
- Flexible LLM Support: Works with OpenAI, Claude, Llama, and other models
- Rich Metadata Filtering: Filter by difficulty, region, dog-friendliness, seasons, etc.
- Conversational Responses: Get detailed explanations, not just lists
- Incremental Updates: Add new trails without rebuilding the entire database
- Extensible Architecture: Easy to add new data sources and features

## Contributing

This project is currently in active development. Contributions, suggestions, and feedback are welcome! Just create an issue and submit your PR!

## License

[License information to be added]
