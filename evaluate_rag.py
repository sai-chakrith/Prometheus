# -*- coding: utf-8 -*-
"""
RAGAS Evaluation Runner
Runs comprehensive evaluation of the RAG system using RAGAS metrics
"""

import os
import sys
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ragas_evaluator import RAGASEvaluator
from src.test_dataset import (
    TEST_CASES,
    QUICK_TEST_QUESTIONS,
    get_test_questions,
    get_questions_with_ground_truth
)


class RAGSystemWrapper:
    """
    Wrapper around your RAG system for evaluation.
    Adapt this to match your actual RAG implementation.
    """
    
    def __init__(self):
        """Initialize RAG system components."""
        try:
            from src.rag import load_vector_index, retrieve, get_embedding_model
            from src.data_loader import load_and_clean_data
            
            print("Loading RAG system components...")
            self.df = load_and_clean_data()
            self.index, self.chunks = load_vector_index()
            self.model = get_embedding_model()
            print("✅ RAG system loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load RAG system: {e}")
            print("   Using mock data for demonstration.")
            self.df = None
            self.index = None
            self.chunks = None
    
    def retrieve(self, query: str, k: int = 5) -> List[tuple]:
        """
        Retrieve relevant contexts for a query.
        
        Returns:
        --------
        List[tuple]
            List of (chunk, distance) tuples
        """
        if self.index is None or self.chunks is None:
            # Mock data for demonstration
            return [
                (f"Mock context 1 for: {query}", 0.1),
                (f"Mock context 2 for: {query}", 0.2),
                (f"Mock context 3 for: {query}", 0.3),
            ]
        
        from src.rag import retrieve
        return retrieve(self.index, self.chunks, query, k)
    
    def generate_answer(self, query: str, contexts: List[str]) -> str:
        """
        Generate answer from contexts.
        
        For now, this creates a simple answer from contexts.
        Replace with your actual LLM-based generation.
        """
        # Simple answer generation (replace with actual LLM call)
        answer = f"Based on the available data:\n\n"
        
        # Extract key information from contexts
        for i, context in enumerate(contexts[:3], 1):
            answer += f"{i}. {context}\n"
        
        answer += f"\nThese are the most relevant funding records for your query: '{query}'"
        
        return answer


def run_evaluation(
    use_quick_test: bool = False,
    export_results: bool = True,
    api_key: str = None
):
    """
    Run RAGAS evaluation on the RAG system.
    
    Parameters:
    -----------
    use_quick_test : bool
        If True, use a smaller test set for faster evaluation
    export_results : bool
        If True, export results to CSV
    api_key : str, optional
        OpenAI API key (can also be set via OPENAI_API_KEY env var)
    """
    print("\n" + "="*70)
    print("🚀 RAGAS EVALUATION FOR RAG SYSTEM")
    print("="*70 + "\n")
    
    # Initialize RAG system
    print("1️⃣  Initializing RAG system...")
    rag_system = RAGSystemWrapper()
    
    # Initialize RAGAS evaluator
    print("\n2️⃣  Initializing RAGAS evaluator...")
    evaluator = RAGASEvaluator(openai_api_key=api_key)
    
    # Get test questions
    print("\n3️⃣  Preparing test dataset...")
    if use_quick_test:
        test_questions = QUICK_TEST_QUESTIONS
        print(f"   Using quick test set: {len(test_questions)} questions")
    else:
        test_cases = TEST_CASES
        test_questions = [tc["question"] for tc in test_cases]
        print(f"   Using full test set: {len(test_questions)} questions")
    
    # Generate answers and collect contexts
    print("\n4️⃣  Running queries through RAG system...")
    questions = []
    answers = []
    contexts_list = []
    ground_truths = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"   Processing {i}/{len(test_questions)}: {question[:50]}...")
        
        # Retrieve contexts
        retrieved = rag_system.retrieve(question, k=5)
        contexts = [chunk for chunk, _ in retrieved]
        
        # Generate answer
        answer = rag_system.generate_answer(question, contexts)
        
        # Find ground truth if available
        ground_truth = None
        if not use_quick_test:
            test_case = next((tc for tc in TEST_CASES if tc["question"] == question), None)
            if test_case:
                ground_truth = test_case.get("ground_truth")
        
        questions.append(question)
        answers.append(answer)
        contexts_list.append(contexts)
        ground_truths.append(ground_truth if ground_truth else "")
    
    # Prepare evaluation dataset
    print("\n5️⃣  Preparing evaluation dataset...")
    dataset = evaluator.prepare_evaluation_dataset(
        questions=questions,
        answers=answers,
        contexts=contexts_list,
        ground_truths=ground_truths if any(ground_truths) else None
    )
    
    # Run evaluation
    print("\n6️⃣  Running RAGAS evaluation...")
    try:
        scores = evaluator.evaluate_dataset(dataset)
        
        # Print results
        evaluator.print_evaluation_report(scores)
        
        # Export results
        if export_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"evaluation_results_{timestamp}.csv"
            evaluator.export_results(scores, dataset, output_path)
        
        return scores
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        print("\nMake sure you have:")
        print("  1. Set OPENAI_API_KEY environment variable")
        print("  2. Installed all dependencies: pip install -r requirements.txt")
        print("  3. Have valid data loaded in your RAG system")
        raise


def run_single_query_evaluation(
    query: str,
    api_key: str = None
):
    """
    Evaluate a single query (useful for debugging).
    
    Parameters:
    -----------
    query : str
        The query to evaluate
    api_key : str, optional
        OpenAI API key
    """
    print(f"\n🔍 Evaluating single query: {query}\n")
    
    # Initialize components
    rag_system = RAGSystemWrapper()
    evaluator = RAGASEvaluator(openai_api_key=api_key)
    
    # Get answer
    retrieved = rag_system.retrieve(query, k=5)
    contexts = [chunk for chunk, _ in retrieved]
    answer = rag_system.generate_answer(query, contexts)
    
    # Evaluate
    scores = evaluator.evaluate_single_query(
        question=query,
        answer=answer,
        contexts=contexts
    )
    
    # Print results
    print("\n📋 Query Details:")
    print(f"   Question: {query}")
    print(f"   Answer: {answer[:200]}...")
    print(f"   Contexts: {len(contexts)} retrieved")
    
    evaluator.print_evaluation_report(scores)
    
    return scores


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation on RAG system")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use quick test set (fewer questions)"
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Don't export results to CSV"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Evaluate a single query instead of full test set"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OpenAI API key not found!")
        print("   Set it via --api-key flag or OPENAI_API_KEY environment variable")
        print("   Some metrics may not work without it.\n")
    
    try:
        if args.query:
            # Single query evaluation
            run_single_query_evaluation(args.query, api_key)
        else:
            # Full evaluation
            run_evaluation(
                use_quick_test=args.quick,
                export_results=not args.no_export,
                api_key=api_key
            )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
