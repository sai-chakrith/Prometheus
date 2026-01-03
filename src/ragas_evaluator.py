# -*- coding: utf-8 -*-
"""
RAGAS Evaluation Module for RAG System
Evaluates the quality of RAG responses using RAGAS metrics
"""

import os
from typing import List, Dict, Any, Optional
import pandas as pd
from datasets import Dataset

# RAGAS imports
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_relevancy,
    answer_correctness,
    answer_similarity
)

# LangChain imports for LLM integration
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings


class RAGASEvaluator:
    """
    RAGAS-based evaluator for RAG system quality assessment.
    
    Metrics:
    --------
    - Faithfulness: Measures factual consistency of answer with context
    - Answer Relevancy: Measures how relevant the answer is to the question
    - Context Precision: Measures signal-to-noise ratio in retrieved context
    - Context Recall: Measures if all relevant info is retrieved
    - Context Relevancy: Measures relevance of retrieved context
    - Answer Correctness: Measures correctness compared to ground truth
    - Answer Similarity: Semantic similarity with ground truth
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize RAGAS evaluator.
        
        Parameters:
        -----------
        openai_api_key : str, optional
            OpenAI API key (defaults to OPENAI_API_KEY env variable)
        model_name : str
            LLM model to use for evaluation
        embedding_model : str
            Embedding model for similarity computations
        """
        # Set API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        elif not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY not set. Set it for full evaluation.")
        
        # Initialize LLM for evaluation
        try:
            self.llm = ChatOpenAI(model_name=model_name, temperature=0)
            print(f"✅ Initialized LLM: {model_name}")
        except Exception as e:
            print(f"⚠️  Could not initialize OpenAI LLM: {e}")
            self.llm = None
        
        # Initialize embeddings
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'}
            )
            print(f"✅ Initialized embeddings: {embedding_model}")
        except Exception as e:
            print(f"⚠️  Could not initialize embeddings: {e}")
            self.embeddings = None
        
        # Define metrics to evaluate
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            context_relevancy,
            answer_correctness,
            answer_similarity
        ]
    
    def prepare_evaluation_dataset(
        self,
        questions: List[str],
        answers: List[str],
        contexts: List[List[str]],
        ground_truths: Optional[List[str]] = None
    ) -> Dataset:
        """
        Prepare evaluation dataset in RAGAS format.
        
        Parameters:
        -----------
        questions : List[str]
            List of user queries/questions
        answers : List[str]
            List of generated answers from RAG system
        contexts : List[List[str]]
            List of retrieved context chunks for each question
        ground_truths : List[str], optional
            List of ground truth answers (required for some metrics)
            
        Returns:
        --------
        Dataset
            HuggingFace Dataset ready for RAGAS evaluation
        """
        data = {
            'question': questions,
            'answer': answers,
            'contexts': contexts,
        }
        
        if ground_truths:
            data['ground_truth'] = ground_truths
        
        return Dataset.from_dict(data)
    
    def evaluate_dataset(
        self,
        dataset: Dataset,
        metrics: Optional[List] = None
    ) -> Dict[str, float]:
        """
        Evaluate a dataset using RAGAS metrics.
        
        Parameters:
        -----------
        dataset : Dataset
            Evaluation dataset with questions, answers, contexts
        metrics : List, optional
            List of RAGAS metrics to use (defaults to all)
            
        Returns:
        --------
        Dict[str, float]
            Dictionary of metric names and scores
        """
        if metrics is None:
            metrics = self.metrics
        
        print("\n🔍 Starting RAGAS evaluation...")
        print(f"📊 Evaluating {len(dataset)} samples")
        print(f"📏 Metrics: {[m.name for m in metrics]}\n")
        
        try:
            # Run evaluation
            results = evaluate(
                dataset=dataset,
                metrics=metrics,
                llm=self.llm,
                embeddings=self.embeddings
            )
            
            print("✅ Evaluation completed successfully!\n")
            
            # Convert results to dict
            scores = {metric.name: results[metric.name] for metric in metrics}
            
            return scores
            
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            raise
    
    def evaluate_single_query(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate a single query-answer pair.
        
        Parameters:
        -----------
        question : str
            User query
        answer : str
            Generated answer
        contexts : List[str]
            Retrieved context chunks
        ground_truth : str, optional
            Ground truth answer
            
        Returns:
        --------
        Dict[str, float]
            Evaluation scores
        """
        # Prepare single-item dataset
        dataset = self.prepare_evaluation_dataset(
            questions=[question],
            answers=[answer],
            contexts=[contexts],
            ground_truths=[ground_truth] if ground_truth else None
        )
        
        return self.evaluate_dataset(dataset)
    
    def print_evaluation_report(self, scores: Dict[str, float]) -> None:
        """
        Print a formatted evaluation report.
        
        Parameters:
        -----------
        scores : Dict[str, float]
            Evaluation scores from evaluate_dataset()
        """
        print("\n" + "="*60)
        print("📊 RAGAS EVALUATION REPORT")
        print("="*60)
        
        # Group metrics by category
        retrieval_metrics = ['context_precision', 'context_recall', 'context_relevancy']
        generation_metrics = ['faithfulness', 'answer_relevancy', 'answer_correctness', 'answer_similarity']
        
        print("\n🔍 RETRIEVAL METRICS:")
        for metric in retrieval_metrics:
            if metric in scores:
                score = scores[metric]
                bar = "█" * int(score * 20)
                print(f"  {metric:20s}: {score:.4f} {bar}")
        
        print("\n📝 GENERATION METRICS:")
        for metric in generation_metrics:
            if metric in scores:
                score = scores[metric]
                bar = "█" * int(score * 20)
                print(f"  {metric:20s}: {score:.4f} {bar}")
        
        # Overall score
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            print("\n" + "-"*60)
            print(f"🎯 OVERALL AVERAGE: {avg_score:.4f}")
            print("="*60 + "\n")
    
    def export_results(
        self,
        scores: Dict[str, float],
        dataset: Dataset,
        output_path: str = "evaluation_results.csv"
    ) -> None:
        """
        Export evaluation results to CSV.
        
        Parameters:
        -----------
        scores : Dict[str, float]
            Evaluation scores
        dataset : Dataset
            Original evaluation dataset
        output_path : str
            Path to save results
        """
        # Convert dataset to DataFrame
        df = pd.DataFrame(dataset)
        
        # Add scores as columns
        for metric_name, score in scores.items():
            df[f'score_{metric_name}'] = score
        
        # Save to CSV
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"💾 Results exported to: {output_path}")


def create_test_dataset_from_rag(
    rag_system,
    test_questions: List[str],
    k: int = 5
) -> Dataset:
    """
    Create a test dataset by running queries through your RAG system.
    
    Parameters:
    -----------
    rag_system : object
        Your RAG system with retrieve() and generate_answer() methods
    test_questions : List[str]
        List of test questions
    k : int
        Number of contexts to retrieve
        
    Returns:
    --------
    Dataset
        Dataset ready for RAGAS evaluation
    """
    questions = []
    answers = []
    contexts_list = []
    
    for question in test_questions:
        # Retrieve contexts
        retrieved = rag_system.retrieve(question, k=k)
        contexts = [chunk for chunk, _ in retrieved]
        
        # Generate answer
        answer = rag_system.generate_answer(question, contexts)
        
        questions.append(question)
        answers.append(answer)
        contexts_list.append(contexts)
    
    return Dataset.from_dict({
        'question': questions,
        'answer': answers,
        'contexts': contexts_list
    })


# Example usage
if __name__ == "__main__":
    print("RAGAS Evaluator Module")
    print("Import this module to evaluate your RAG system")
    print("\nExample:")
    print("  from src.ragas_evaluator import RAGASEvaluator")
    print("  evaluator = RAGASEvaluator()")
    print("  scores = evaluator.evaluate_single_query(...)")
