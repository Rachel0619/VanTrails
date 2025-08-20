#!/usr/bin/env python3
"""
Evaluate generation quality using LLM-as-a-Judge
"""

import os
import sys
import pandas as pd
import json
from tqdm import tqdm

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.workflows.recommend_trails import recommend_trails
from src.llm.client import llm_function

IMPROVED_JUDGE_PROMPT = """
You will be given a user_question and system_answer couple.
Your task is to provide a 'total rating' scoring how well the system_answer answers the user concerns expressed in the user_question.
Give your answer on a scale of 1 to 4, where 1 means that the system_answer is not helpful at all, and 4 means that the system_answer completely and helpfully addresses the user_question.

Here is the scale you should use to build your answer:
1: The system_answer is terrible: completely irrelevant to the question asked, or very partial
2: The system_answer is mostly not helpful: misses some key aspects of the question
3: The system_answer is mostly helpful: provides support, but still could be improved
4: The system_answer is excellent: relevant, direct, detailed, and addresses all the concerns raised in the question

Provide your feedback as follows:

Feedback:::
Evaluation: (your rationale for the rating, as a text)
Total rating: (your rating, as a number between 1 and 4)

You MUST provide values for 'Evaluation:' and 'Total rating:' in your answer.

Now here are the question and answer.

Question: {question}
Answer: {answer}

Provide your feedback.
Feedback:::
Evaluation: """

def evaluate_response(question: str) -> dict:
    """Evaluate a response using LLM-as-a-Judge"""
    try:
        answer_generator = recommend_trails(question)
        answer = ""
        for chunk in answer_generator:
            answer = chunk  # Keep only the latest (complete) response
        judge_prompt = IMPROVED_JUDGE_PROMPT.format(question=question, answer=answer)
        system_prompt = "You are an expert evaluator of AI system responses. Provide fair and accurate ratings."
        evaluation = llm_function(judge_prompt, system_prompt, stream=False)
        
        # Extract rating from the evaluation
        rating = None
        evaluation_text = ""
        
        if "Total rating:" in evaluation:
            lines = evaluation.split('\n')
            for line in lines:
                if line.strip().startswith("Total rating:"):
                    try:
                        rating = int(line.split(":")[-1].strip())
                    except:
                        pass
                elif line.strip().startswith("Evaluation:"):
                    evaluation_text = line.split(":", 1)[-1].strip()
        
        return {
            "query": question,
            "answer": answer,
            "rating": rating,
            "evaluation_text": evaluation_text,
        }
    except Exception as e:
        return {
            "query": question,
            "answer": answer,
            "rating": None,
            "evaluation_text": f"Error in evaluation: {e}",
        }

def main():
    """Run generation evaluation"""
    print("Starting generation evaluation...")
    
    test_df = pd.read_csv("../query_parser/query_parser_test.csv")
    queries = test_df.loc[:20, 'user_query'].tolist()

    print(f"Evaluating {len(queries)} queries...")
    
    results = []
    
    for query in tqdm(queries, desc="Generating and evaluating responses"):
        try:
            # Evaluate response
            evaluation = evaluate_response(query)
            
            result = {
                'query': query,
                'answer': evaluation['answer'],
                'rating': evaluation['rating'],
                'evaluation_text': evaluation['evaluation_text'],
            }
            
            results.append(result)
            print(f"Rating: {evaluation['rating']}")
            
        except Exception as e:
            print(f"Error processing query: {e}")
            results.append({
                'query': query,
                'answer': f"Error: {e}",
                'rating': None,
                'evaluation_text': f"Error: {e}",
            })
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv("generation_evaluation_results.csv", index=False)
    
    # Calculate statistics
    valid_ratings = [r for r in results_df['rating'] if r is not None]
    if valid_ratings:
        avg_rating = sum(valid_ratings) / len(valid_ratings)
        rating_counts = {i: valid_ratings.count(i) for i in range(1, 5)}
        
        print(f"\n{'='*50}")
        print("GENERATION EVALUATION RESULTS")
        print(f"{'='*50}")
        print(f"Total queries evaluated: {len(results)}")
        print(f"Valid ratings: {len(valid_ratings)}")
        print(f"Average rating: {avg_rating:.2f}/4")
        print(f"Rating distribution:")
        for rating, count in rating_counts.items():
            percentage = (count / len(valid_ratings)) * 100
            print(f"  {rating}/4: {count} ({percentage:.1f}%)")
        print(f"{'='*50}")
    
    print(f"\nResults saved to: generation_evaluation_results.csv")

if __name__ == "__main__":
    main()