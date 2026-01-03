# -*- coding: utf-8 -*-
"""
Batch RAGAS Evaluation
Compare multiple RAG configurations or track improvements over time
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_rag import run_evaluation, RAGSystemWrapper
from src.ragas_evaluator import RAGASEvaluator


class BatchEvaluator:
    """Run multiple evaluations and compare results."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize batch evaluator.
        
        Parameters:
        -----------
        api_key : str, optional
            OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.results = []
    
    def run_experiment(
        self,
        name: str,
        config: Dict[str, Any],
        use_quick_test: bool = True
    ) -> Dict[str, float]:
        """
        Run a single experiment with given configuration.
        
        Parameters:
        -----------
        name : str
            Experiment name/identifier
        config : Dict[str, Any]
            Configuration parameters (for future use)
        use_quick_test : bool
            Use quick test set
            
        Returns:
        --------
        Dict[str, float]
            Evaluation scores
        """
        print(f"\n{'='*70}")
        print(f"🧪 Running Experiment: {name}")
        print(f"{'='*70}\n")
        print(f"Config: {config}")
        
        try:
            scores = run_evaluation(
                use_quick_test=use_quick_test,
                export_results=False,
                api_key=self.api_key
            )
            
            # Store results
            result = {
                'experiment': name,
                'timestamp': datetime.now().isoformat(),
                'config': config,
                'scores': scores
            }
            self.results.append(result)
            
            print(f"\n✅ Experiment '{name}' completed!")
            print(f"   Average Score: {sum(scores.values()) / len(scores):.4f}")
            
            return scores
            
        except Exception as e:
            print(f"\n❌ Experiment '{name}' failed: {e}")
            return {}
    
    def compare_results(self) -> pd.DataFrame:
        """
        Compare results from all experiments.
        
        Returns:
        --------
        pd.DataFrame
            Comparison table
        """
        if not self.results:
            print("No results to compare!")
            return pd.DataFrame()
        
        # Prepare comparison data
        comparison_data = []
        for result in self.results:
            row = {
                'Experiment': result['experiment'],
                'Timestamp': result['timestamp'],
            }
            # Add all metric scores
            for metric, score in result['scores'].items():
                row[metric] = score
            # Add average
            if result['scores']:
                row['Average'] = sum(result['scores'].values()) / len(result['scores'])
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        return df
    
    def print_comparison(self):
        """Print a formatted comparison table."""
        df = self.compare_results()
        
        if df.empty:
            return
        
        print("\n" + "="*100)
        print("📊 BATCH EVALUATION COMPARISON")
        print("="*100)
        print("\n")
        print(df.to_string(index=False))
        print("\n" + "="*100)
        
        # Find best experiment
        if 'Average' in df.columns:
            best_idx = df['Average'].idxmax()
            best_exp = df.loc[best_idx, 'Experiment']
            best_score = df.loc[best_idx, 'Average']
            print(f"\n🏆 Best Experiment: {best_exp} (Average: {best_score:.4f})")
            print("="*100 + "\n")
    
    def export_comparison(self, output_path: str = None):
        """
        Export comparison results to CSV and JSON.
        
        Parameters:
        -----------
        output_path : str, optional
            Base path for output files
        """
        if not self.results:
            print("No results to export!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_path is None:
            output_path = f"batch_evaluation_{timestamp}"
        
        # Export DataFrame to CSV
        df = self.compare_results()
        csv_path = f"{output_path}.csv"
        df.to_csv(csv_path, index=False)
        print(f"💾 CSV exported to: {csv_path}")
        
        # Export full results to JSON
        json_path = f"{output_path}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON exported to: {json_path}")


def run_baseline_vs_improved_comparison():
    """
    Example: Compare baseline system vs improved version.
    """
    evaluator = BatchEvaluator()
    
    # Experiment 1: Baseline
    evaluator.run_experiment(
        name="Baseline",
        config={
            "retrieval_k": 5,
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        },
        use_quick_test=True
    )
    
    # Experiment 2: Improved retrieval (more contexts)
    evaluator.run_experiment(
        name="More_Contexts",
        config={
            "retrieval_k": 10,
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        },
        use_quick_test=True
    )
    
    # Experiment 3: Better embeddings
    evaluator.run_experiment(
        name="Better_Embeddings",
        config={
            "retrieval_k": 5,
            "model": "intfloat/multilingual-e5-large"
        },
        use_quick_test=True
    )
    
    # Compare results
    evaluator.print_comparison()
    evaluator.export_comparison("comparison_baseline_vs_improved")


def run_ablation_study():
    """
    Example: Ablation study - test impact of different components.
    """
    evaluator = BatchEvaluator()
    
    experiments = [
        ("Full_System", {"all_features": True}),
        ("No_Reranking", {"reranking": False}),
        ("No_Query_Expansion", {"query_expansion": False}),
        ("Minimal", {"reranking": False, "query_expansion": False}),
    ]
    
    for name, config in experiments:
        evaluator.run_experiment(name, config, use_quick_test=True)
    
    evaluator.print_comparison()
    evaluator.export_comparison("ablation_study")


def run_daily_monitoring():
    """
    Example: Daily monitoring - track performance over time.
    """
    evaluator = BatchEvaluator()
    
    # Run today's evaluation
    today = datetime.now().strftime("%Y-%m-%d")
    evaluator.run_experiment(
        name=f"Daily_{today}",
        config={"date": today, "version": "production"},
        use_quick_test=False  # Use full test for monitoring
    )
    
    # Export with timestamp
    evaluator.export_comparison(f"daily_monitoring_{today}")
    
    # Could append to historical log here
    print("\n📈 Daily monitoring complete. Check historical trends.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run batch RAGAS evaluation")
    parser.add_argument(
        "--mode",
        choices=["compare", "ablation", "daily"],
        default="compare",
        help="Evaluation mode"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OpenAI API key not found!")
        print("   Set via --api-key flag or OPENAI_API_KEY env var\n")
    
    # Run selected mode
    if args.mode == "compare":
        print("\n🔬 Running Baseline vs Improved Comparison...\n")
        run_baseline_vs_improved_comparison()
    
    elif args.mode == "ablation":
        print("\n🔬 Running Ablation Study...\n")
        run_ablation_study()
    
    elif args.mode == "daily":
        print("\n📊 Running Daily Monitoring...\n")
        run_daily_monitoring()
