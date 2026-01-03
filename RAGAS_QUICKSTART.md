# 🎯 Quick Start Guide - RAGAS Evaluation

Get started with RAGAS evaluation in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set OpenAI API Key

**Option A - Environment Variable (Recommended)**
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B - .env File**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
# OPENAI_API_KEY=sk-your-api-key-here
```

## Step 3: Run Your First Evaluation

### Quick Test (3 questions, ~30 seconds)
```bash
python evaluate_rag.py --quick
```

### Full Evaluation (all test questions)
```bash
python evaluate_rag.py
```

### Test a Single Query
```bash
python evaluate_rag.py --query "Which fintech startups got funding in Karnataka?"
```

## 📊 What You'll See

```
🚀 RAGAS EVALUATION FOR RAG SYSTEM
================================================

1️⃣  Initializing RAG system...
✅ RAG system loaded successfully!

2️⃣  Initializing RAGAS evaluator...
✅ Initialized LLM: gpt-3.5-turbo

3️⃣  Preparing test dataset...
   Using quick test set: 3 questions

4️⃣  Running queries through RAG system...
   Processing 1/3: Which fintech startups...
   Processing 2/3: What was the total...
   Processing 3/3: कर्नाटक में फंडिंग...

5️⃣  Preparing evaluation dataset...

6️⃣  Running RAGAS evaluation...
📊 Evaluating 3 samples
📏 Metrics: [faithfulness, answer_relevancy, ...]

✅ Evaluation completed successfully!

============================================================
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

------------------------------------------------------------
🎯 OVERALL AVERAGE: 0.8229
============================================================

💾 Results exported to: evaluation_results_20260103_143022.csv
```

## 🎓 Understanding Your Scores

| Score Range | Quality | Action |
|------------|---------|--------|
| 0.8 - 1.0 | Excellent ✅ | Keep it up! |
| 0.6 - 0.8 | Good 👍 | Minor tweaks |
| 0.4 - 0.6 | Fair ⚠️ | Needs improvement |
| < 0.4 | Poor ❌ | Requires attention |

## 🔧 Common Issues

### "OpenAI API Key not found"
**Solution**: Set the environment variable
```powershell
$env:OPENAI_API_KEY="your-key"
```

### "Module 'ragas' not found"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "Vector index not found"
**Solution**: Make sure your RAG system is set up with data
```python
from src.rag import build_vector_index
from src.data_loader import load_and_clean_data

df = load_and_clean_data()
index, chunks = build_vector_index(df)
```

## 📚 Next Steps

1. ✅ Run quick evaluation
2. 📖 Read detailed guide: [RAGAS_GUIDE.md](RAGAS_GUIDE.md)
3. 🧪 Add your own test cases: Edit `src/test_dataset.py`
4. 🎯 Improve your scores: Optimize retrieval and generation
5. 📊 Track progress: Compare results over time

## 💡 Pro Tips

1. **Start Small**: Use `--quick` flag first
2. **Monitor Costs**: Each evaluation costs ~$0.01-$0.20
3. **Baseline First**: Run initial evaluation before making changes
4. **Iterate**: Make small improvements and re-evaluate
5. **Track Results**: Keep CSV exports for comparison

## 🎯 Evaluation Workflow

```
1. Baseline Evaluation
   ↓
2. Identify Weak Metrics
   ↓
3. Make Improvements
   ↓
4. Re-evaluate
   ↓
5. Compare Results
   ↓
6. Repeat!
```

## 📞 Need Help?

- 📖 Full Guide: [RAGAS_GUIDE.md](RAGAS_GUIDE.md)
- 🔧 Code: Check `src/ragas_evaluator.py`
- 🧪 Tests: See `src/test_dataset.py`
- 📊 Runner: Check `evaluate_rag.py`

---

**Ready to improve your RAG system? Let's go! 🚀**
