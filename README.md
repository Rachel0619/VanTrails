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

The code I used to scrape this dataset from the Internet can be found at [scraper.py](src/scrapers/scraper.py).

## Technologies

- Qdrant for vector database and semantic search
- GPT-5-mini as an LLM
- FLASK for REST API
- Gradio for user interface
- Docker for containerization

## Getting Started

### Prerequisites
- Python 3.12+
- Docker
- OpenAI API key (or other LLM provider)

### Preparation

#### Set up environment variables

rename `.env.example` to `.env` and then replace OpenAI API with your own.

#### Docker

```bash
$ docker-compose build
$ docker-compose up -d
```

If it's your first time running this app, you also need to ingest the entire dataset by running this command before perfoming any search task.

```bash
$ docker-compose --profile tools run --rm vantrails-ingest
```

Then you can check the accessibility of FlaskAPI and Gradio interface by navigating to these sites:
- FlaskAPI: http://localhost:8000/health
- Gradio: http://localhost:7860

### Using the application

#### Flask API

```bash
URL=http://localhost:8000
QUERY="Replace this with the question you want to ask"
DATA='{
    "query": "'${QUERY}'"
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${DATA}" \
    ${URL}/api/recommend
```

#### Gradio Interface

You can also interact with this RAG system by Gradio.

Navigate to [local URL](http://127.0.0.1:7860) and ask questions.

## Evaluation

You can find a detailed explanation for the evaluation methodologies I used for this project at [README.md](evaluation/README.md)

## Contributing

This project is currently in active development. Contributions, suggestions, and feedback are welcome! Just create an issue and submit your PR!

## License

This project uses MIT license.

## Future improvements

- improve the front end, make it more aesthetically appealing and perhaps more interactive
- more prompting to improve the output format for final response
- try hybrid search and document reranking
- add edge cases for evaluation (no filter, no search result, etc.)
