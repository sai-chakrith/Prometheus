# RAGAS Evaluation for RAG System

## Overview

RAGAS (Retrieval Augmented Generation Assessment) has been implemented to evaluate the quality of your RAG system. This implementation provides comprehensive metrics to assess both retrieval and generation components.

## 📊 Metrics Implemented

### Retrieval Metrics
- **Context Precision**: Measures the signal-to-noise ratio in retrieved contexts
- **Context Recall**: Evaluates if all relevant information is retrieved
- **Context Relevancy**: Assesses the relevance of retrieved contexts to the query

### Generation Metrics
- **Faithfulness**: Measures factual consistency of answers with retrieved context
- **Answer Relevancy**: Evaluates how relevant the answer is to the question
- **Answer Correctness**: Compares generated answer with ground truth (when available)
- **Answer Similarity**: Semantic similarity with ground truth answers

## 🚀 Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set OpenAI API Key** (required for most metrics):
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

## 📝 Usage

### Quick Start - Full Evaluation

Run evaluation on the complete test set:

```bash
python evaluate_rag.py
```

### Quick Test (Faster)

Use a smaller test set for faster evaluation:

```bash
python evaluate_rag.py --quick
```

### Single Query Evaluation

Test a specific query:

```bash
python evaluate_rag.py --query "Which fintech startups received funding in Karnataka?"
```

### Custom API Key

Provide API key via command line:

```bash
python evaluate_rag.py --api-key "your-api-key-here"
```

### Don't Export Results

Skip CSV export:

```bash
python evaluate_rag.py --no-export
```

## 🔧 Programmatic Usage

### Basic Evaluation

```python
from src.ragas_evaluator import RAGASEvaluator
from datasets import Dataset

# Initialize evaluator
evaluator = RAGASEvaluator(
    openai_api_key="your-key",
    model_name="gpt-3.5-turbo"
)

# Prepare data
dataset = evaluator.prepare_evaluation_dataset(
    questions=["What is AI?"],
    answers=["AI is artificial intelligence..."],
    contexts=[["AI stands for...", "Machine learning..."]]
)

# Evaluate
scores = evaluator.evaluate_dataset(dataset)

# Print report
evaluator.print_evaluation_report(scores)
```

### Single Query Evaluation

```python
from src.ragas_evaluator import RAGASEvaluator

evaluator = RAGASEvaluator()

scores = evaluator.evaluate_single_query(
    question="What is machine learning?",
    answer="Machine learning is a subset of AI...",
    contexts=["ML is a method...", "AI encompasses..."],
    ground_truth="Machine learning is..." # Optional
)

evaluator.print_evaluation_report(scores)
```

### Custom Metrics

```python
from ragas.metrics import faithfulness, answer_relevancy
from src.ragas_evaluator import RAGASEvaluator

evaluator = RAGASEvaluator()

# Use only specific metrics
scores = evaluator.evaluate_dataset(
    dataset,
    metrics=[faithfulness, answer_relevancy]
)
```

## 📂 File Structure

```
Prometheus/
├── src/
│   ├── ragas_evaluator.py    # Main RAGAS evaluation module
│   ├── test_dataset.py        # Test questions and ground truth
│   ├── rag.py                 # Your RAG implementation
│   └── data_loader.py         # Data loading utilities
├── evaluate_rag.py            # Evaluation runner script
├── requirements.txt           # Dependencies (updated with RAGAS)
└── RAGAS_GUIDE.md            # This file
```

## 🧪 Test Dataset

The test dataset (`src/test_dataset.py`) includes:

- **5 full test cases** with metadata
- **English and Hindi queries**
- **RAG and Analytics query types**
- **Ground truth answers** for some queries
- **Expected context keywords**

### Adding Custom Test Cases

Edit `src/test_dataset.py`:

```python
TEST_CASES.append({
    "id": 6,
    "question": "Your custom question?",
    "language": "en",
    "intent": "rag",
    "filters": {"sector": "fintech"},
    "ground_truth": "Expected answer..."
})
```

## 📊 Understanding Results

### Score Interpretation

All metrics range from **0 to 1** (higher is better):

- **0.8 - 1.0**: Excellent
- **0.6 - 0.8**: Good
- **0.4 - 0.6**: Fair (needs improvement)
- **< 0.4**: Poor (requires attention)

### Sample Output

```
📊 RAGAS EVALUATION REPORT
============================================================

🔍 RETRIEVAL METRICS:
  context_precision   : 0.8542 ████████████████
  context_recall      : 0.7891 ███████████████
  context_relevancy   : 0.8123 ████████████████

📝 GENERATION METRICS:
  faithfulness        : 0.9156 ██████████████████
  answer_relevancy    : 0.8234 ████████████████
  answer_correctness  : 0.7645 ███████████████
  answer_similarity   : 0.8012 ████████████████

------------------------------------------------------------
🎯 OVERALL AVERAGE: 0.8229
============================================================
```

## 🔍 Troubleshooting

### Error: OpenAI API Key Not Found

**Solution**: Set the environment variable:
```bash
$env:OPENAI_API_KEY="sk-..."
```

### Error: Module 'ragas' not found

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Error: Vector index not found

**Solution**: Build the vector index first:
```python
from src.rag import build_vector_index
from src.data_loader import load_and_clean_data

df = load_and_clean_data()
index, chunks = build_vector_index(df)
```

### Slow Evaluation

**Solutions**:
1. Use `--quick` flag for smaller test set
2. Use faster LLM model: `model_name="gpt-3.5-turbo"`
3. Reduce number of metrics
4. Limit test cases in `test_dataset.py`

## 🎯 Best Practices

1. **Start with Quick Test**: Use `--quick` flag initially
2. **Monitor Costs**: OpenAI API calls incur costs
3. **Baseline First**: Run initial evaluation to establish baseline
4. **Iterate**: Make improvements and re-evaluate
5. **Track Results**: Export CSV results for comparison over time
6. **Use Ground Truth**: Add ground truth for more accurate metrics

## 📈 Continuous Evaluation

### Automated Evaluation Pipeline

Create a script to run regular evaluations:

```python
# continuous_eval.py
import schedule
import time
from evaluate_rag import run_evaluation

def daily_evaluation():
    print("Running daily evaluation...")
    scores = run_evaluation(use_quick_test=True)
    # Log scores to database or monitoring system
    print(f"Daily scores: {scores}")

# Run every day at 2 AM
schedule.every().day.at("02:00").do(daily_evaluation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/evaluate.yml
name: RAG Evaluation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python evaluate_rag.py --quick
```

## 🔗 Resources

- [RAGAS Documentation](https://docs.ragas.io/)
- [RAGAS GitHub](https://github.com/explodinggradients/ragas)
- [LangChain Documentation](https://python.langchain.com/)

## 💡 Advanced Usage

### Custom Evaluation Metrics

Create your own metrics:

```python
from ragas.metrics import Metric

class CustomMetric(Metric):
    def __init__(self):
        self.name = "custom_metric"
    
    def score(self, row):
        # Your custom scoring logic
        return score

# Use in evaluation
evaluator.metrics.append(CustomMetric())
```

### Batch Evaluation

Evaluate multiple RAG system versions:

```python
versions = ["v1", "v2", "v3"]
results = {}

for version in versions:
    rag_system = load_rag_version(version)
    scores = run_evaluation(rag_system)
    results[version] = scores

# Compare results
compare_versions(results)
```

## 📞 Support

For issues or questions:
1. Check this guide
2. Review RAGAS documentation
3. Check test dataset examples
4. Review error messages carefully

---

**Happy Evaluating! 🎉**
