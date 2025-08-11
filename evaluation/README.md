## Evaluation

I evaluated three parts of this RAG system:
- query_parser
- retrieval
- generation

### Query Parser

The [`query_parser`](../src/processing/query_parser.py) transforms natural language queries into JSON format filters that are used in the first step of [`vector_search`](../src/rag/vector_search.py).

For example, when processing a query like "Could you suggest an easy, family-friendly walk that's stroller-accessible, stretches for at least 8 km, but doesn't take more than 3 hours to complete", the `query_parser` is expected to output `{"difficulty":"Easy","time_max":3,"distance_min":8}`. This JSON is then used as a metadata filter for Qdrant vector search.

I used [Promptfoo](https://www.promptfoo.dev/), an open-source CLI and library for evaluating and red-teaming LLM applications, to evaluate different combinations of prompts and LLMs.

All tested prompts can be found in [`prompt.py`](prompts.py), while the tested LLMs are configured in [`promptfooconfig.yaml`](promptfooconfig.yaml).

Based on the evaluation results, `prompt_v2` combined with `GPT-5-mini` were selected to implement the `query_parser` functionality.


### Retrieval



### Generation


