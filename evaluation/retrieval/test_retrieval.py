import os
import sys
import pandas as pd
import re
from tqdm import tqdm
# Suppress HuggingFace warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.rag.vector_search import TrailVectorDB
from src.processing.query_parser import QueryParser
from src.llm.client import llm_function

# load vector database
vector_db = TrailVectorDB()
is_new_collection = vector_db.create_collection()
csv_path = "../../data/vancouver_trails_clean.csv"
final_count = vector_db.ingest_trails(csv_path)

# load test data
test_df = pd.read_csv("../query_parser/query_parser_test.csv")
queries = test_df['user_query']

query_parser = QueryParser()
retreival_test_result = []

for query in tqdm(queries[:50], desc="Processing queries"):
   filters_dict = query_parser.parse_query_with_llm(query, llm_function)
   qdrant_filter = vector_db.build_qdrant_filter(filters_dict)
   results = vector_db.search_trails(query, limit=3)
   payload_keys = re.findall(r"key='([^']*)'", str(qdrant_filter))
   for i, result in enumerate(results, 1):
       filtered_payload = {key: result.payload.get(key) for key in payload_keys}
       retreival_test_result.append({
           'query': query,
           'filters_dict': filters_dict,
           'qdrant_filter': qdrant_filter,
           'payload': filtered_payload
       })
   
print("=" * 50)
print(f"Completed evaluation. Results can be found in test_retrieval_result.csv")
print("=" * 50)

retreival_test_result = pd.DataFrame(retreival_test_result)
retreival_test_result.to_csv("test_retrieval_result.csv", index=False)

