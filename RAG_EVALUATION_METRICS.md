# 📊 RAG System Evaluation Metrics - Complete Guide

> **For:** Understanding how we measure the quality of AI-generated answers
> **Last Updated:** January 2026

---

## 📖 Table of Contents

1. [What Are Evaluation Metrics?](#-what-are-evaluation-metrics)
2. [Why Do We Need Them?](#-why-do-we-need-them)
3. [Overview of RAG Evaluation](#-overview-of-rag-evaluation)
4. [Retrieval Metrics](#-retrieval-metrics)
5. [Generation Metrics](#-generation-metrics)
6. [End-to-End Metrics](#-end-to-end-metrics)
7. [Prometheus-Specific Metrics](#-prometheus-specific-metrics)
8. [How to Interpret Scores](#-how-to-interpret-scores)
9. [Real-World Examples](#-real-world-examples)
10. [Best Practices](#-best-practices)

---

## 🤔 What Are Evaluation Metrics?

### In Simple Terms

Evaluation metrics are like **report cards** for AI systems. Just like how teachers grade your exam answers, these metrics grade how well the AI:
- Finds the right information (Retrieval)
- Generates accurate answers (Generation)
- Helps users solve their problems (Overall Quality)

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM EVALUATION                         │
│                                                                  │
│  ┌──────────────────┐   ┌──────────────────┐   ┌─────────────┐ │
│  │   RETRIEVAL      │   │   GENERATION     │   │  END-TO-END │ │
│  │                  │   │                  │   │             │ │
│  │ Did we find the  │   │ Did we create a  │   │ Did we help │ │
│  │ right documents? │   │ good answer?     │   │ the user?   │ │
│  │                  │   │                  │   │             │ │
│  │ Metrics:         │   │ Metrics:         │   │ Metrics:    │ │
│  │ • Precision      │   │ • Faithfulness   │   │ • Answer    │ │
│  │ • Recall         │   │ • Relevance      │   │   Quality   │ │
│  │ • MRR            │   │ • Coherence      │   │ • Latency   │ │
│  │ • NDCG           │   │ • Completeness   │   │ • User      │ │
│  └──────────────────┘   └──────────────────┘   │   Feedback  │ │
│                                                 └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Why Do We Need Them?

### Problems Without Metrics

Imagine if:
- AI says "Top 10 startups" but only shows 5 → **Incomplete**
- AI invents fake funding amounts → **Hallucination**
- AI takes 30 seconds to respond → **Too Slow**
- AI gives unrelated information → **Irrelevant**

### What Metrics Help Us Do

| Goal | Metric Used | Example |
|------|-------------|---------|
| Find accurate info | Precision | 9/10 retrieved docs were relevant |
| Don't miss info | Recall | Found 8/10 relevant docs in DB |
| Speed matters | Latency | Response in 2.5 seconds |
| Factual answers | Faithfulness | No hallucinations detected |
| User satisfaction | Answer Quality | 4.5/5 star rating |

---

## 🔍 Overview of RAG Evaluation

### The Three Stages

```
STAGE 1: RETRIEVAL                    STAGE 2: GENERATION
──────────────────                    ───────────────────
Query → Search DB                     Context + Query → LLM
        ↓                                     ↓
   Get top-K docs                       Generate answer
        ↓                                     ↓
   Are they relevant? ✓                 Is it accurate? ✓


                    STAGE 3: END-TO-END
                    ───────────────────
                    Full pipeline test
                           ↓
                    Does it help user? ✓
```

---

## 📥 Retrieval Metrics

### 1. Precision

#### Layman Explanation

**Precision** = "Of everything we retrieved, how much was actually useful?"

Think of it like fishing:
- You cast a net and catch 10 fish
- But only 7 are the type you wanted
- **Precision = 7/10 = 70%**

#### Example in Prometheus

```
User asks: "Top fintech startups in Bangalore"

Retrieved 50 documents:
✅ 40 are about fintech in Bangalore
❌ 10 are about other sectors/cities

Precision = 40/50 = 0.80 = 80%
```

#### Mathematical Formula

$$
\text{Precision} = \frac{\text{Relevant Retrieved Documents}}{\text{Total Retrieved Documents}}
$$

$$
P = \frac{|\text{Relevant} \cap \text{Retrieved}|}{|\text{Retrieved}|}
$$

#### Python Code

```python
def precision(retrieved_docs, relevant_docs):
    """
    Calculate precision score
    
    Args:
        retrieved_docs: List of retrieved document IDs
        relevant_docs: List of actually relevant document IDs
    
    Returns:
        Float between 0 and 1
    """
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    
    true_positives = len(retrieved_set & relevant_set)
    total_retrieved = len(retrieved_set)
    
    if total_retrieved == 0:
        return 0.0
    
    return true_positives / total_retrieved

# Example
retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
relevant = ['doc1', 'doc2', 'doc6', 'doc7']

p = precision(retrieved, relevant)
print(f"Precision: {p}")  # Output: 0.4 (2/5)
```

#### When to Use

- When **false positives are costly** (showing wrong info is bad)
- When you want **high-quality results**
- Example: Medical diagnosis, legal documents

---

### 2. Recall

#### Layman Explanation

**Recall** = "Of all the relevant stuff out there, how much did we find?"

Think of it like a treasure hunt:
- There are 10 hidden treasures
- You found 8 of them
- **Recall = 8/10 = 80%**

#### Example in Prometheus

```
Database has 100 fintech startups in Bangalore

Retrieved 50 documents:
✅ 40 are actually fintech in Bangalore
❌ Missed 60 other fintech startups in DB

Recall = 40/100 = 0.40 = 40%
```

#### Mathematical Formula

$$
\text{Recall} = \frac{\text{Relevant Retrieved Documents}}{\text{Total Relevant Documents in Database}}
$$

$$
R = \frac{|\text{Relevant} \cap \text{Retrieved}|}{|\text{Relevant}|}
$$

#### Python Code

```python
def recall(retrieved_docs, relevant_docs):
    """
    Calculate recall score
    
    Args:
        retrieved_docs: List of retrieved document IDs
        relevant_docs: List of all relevant documents (ground truth)
    
    Returns:
        Float between 0 and 1
    """
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    
    true_positives = len(retrieved_set & relevant_set)
    total_relevant = len(relevant_set)
    
    if total_relevant == 0:
        return 0.0
    
    return true_positives / total_relevant

# Example
retrieved = ['doc1', 'doc2', 'doc3']
relevant = ['doc1', 'doc2', 'doc4', 'doc5', 'doc6']

r = recall(retrieved, relevant)
print(f"Recall: {r}")  # Output: 0.4 (2/5)
```

#### When to Use

- When **missing information is costly** (can't afford to miss anything)
- When you want **comprehensive results**
- Example: Search engines, medical screening

---

### 3. F1 Score

#### Layman Explanation

**F1 Score** = "The balanced average of Precision and Recall"

Problem: High precision but low recall (or vice versa) isn't good
Solution: F1 Score balances both!

Think of it like:
- Precision = Quality of results
- Recall = Quantity of results
- F1 = Best of both worlds

#### Mathematical Formula

$$
F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
$$

This is the **harmonic mean** (not regular average).

Why harmonic mean? Because it punishes extreme values:
- If Precision = 100% but Recall = 10%, regular average = 55% (misleading!)
- F1 Score = 18% (more realistic!)

#### Python Code

```python
def f1_score(precision, recall):
    """
    Calculate F1 score
    
    Args:
        precision: Precision value (0-1)
        recall: Recall value (0-1)
    
    Returns:
        Float between 0 and 1
    """
    if precision + recall == 0:
        return 0.0
    
    return 2 * (precision * recall) / (precision + recall)

# Example
p = 0.8  # 80% precision
r = 0.6  # 60% recall

f1 = f1_score(p, r)
print(f"F1 Score: {f1}")  # Output: 0.686
```

#### Comparison Table

| Precision | Recall | F1 Score | Interpretation |
|-----------|--------|----------|----------------|
| 90% | 90% | **90%** | Excellent! |
| 100% | 50% | **67%** | High quality, low coverage |
| 50% | 100% | **67%** | Low quality, high coverage |
| 30% | 30% | **30%** | Poor overall |

---

### 4. Mean Reciprocal Rank (MRR)

#### Layman Explanation

**MRR** = "How soon do we show the correct answer?"

Imagine a quiz show:
- If correct answer is 1st option → Score = 1/1 = 1.0 ⭐⭐⭐⭐⭐
- If correct answer is 2nd option → Score = 1/2 = 0.5 ⭐⭐⭐
- If correct answer is 5th option → Score = 1/5 = 0.2 ⭐

#### Example in Prometheus

```
Query: "Swiggy funding amount"

Retrieved documents (in order):
1. About Zomato ❌
2. About Swiggy ✅ ← First relevant at position 2

Reciprocal Rank = 1/2 = 0.5

If we have 10 queries:
Query 1: First relevant at position 1 → RR = 1.0
Query 2: First relevant at position 3 → RR = 0.33
Query 3: First relevant at position 2 → RR = 0.5
...
Query 10: First relevant at position 1 → RR = 1.0

MRR = Average of all RR = (1.0 + 0.33 + 0.5 + ... + 1.0) / 10
```

#### Mathematical Formula

$$
\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}
$$

Where:
- $|Q|$ = number of queries
- $\text{rank}_i$ = position of first relevant document for query $i$

#### Python Code

```python
def mrr(queries_results):
    """
    Calculate Mean Reciprocal Rank
    
    Args:
        queries_results: List of lists, where each inner list is
                        [doc1_relevant, doc2_relevant, doc3_relevant, ...]
                        with True/False values
    
    Returns:
        Float between 0 and 1
    """
    reciprocal_ranks = []
    
    for results in queries_results:
        for i, is_relevant in enumerate(results):
            if is_relevant:
                reciprocal_ranks.append(1.0 / (i + 1))  # +1 because index starts at 0
                break
        else:
            reciprocal_ranks.append(0.0)  # No relevant doc found
    
    return sum(reciprocal_ranks) / len(reciprocal_ranks)

# Example
queries = [
    [False, True, False],   # First relevant at position 2 → RR = 1/2
    [True, False, False],   # First relevant at position 1 → RR = 1/1
    [False, False, True],   # First relevant at position 3 → RR = 1/3
]

score = mrr(queries)
print(f"MRR: {score:.3f}")  # Output: 0.611
```

#### When to Use

- When **ranking matters** (position of results is important)
- Search engines, recommendation systems
- Prometheus: User wants answer fast (top results matter most)

---

### 5. Normalized Discounted Cumulative Gain (NDCG)

#### Layman Explanation

**NDCG** = "How good is our ranking, considering both relevance AND position?"

Think of a podium:
```
        🥇 1st Place (worth 10 points if relevant)
       🥈  2nd Place (worth 7 points if relevant)
      🥉   3rd Place (worth 5 points if relevant)
     4️⃣    4th Place (worth 3 points if relevant)
```

Better documents at top = Higher score!

#### The Concept

1. **Cumulative Gain (CG)**: Sum of relevance scores
2. **Discounted** (DCG): Relevance divided by position (top positions matter more)
3. **Normalized** (NDCG): Compare to perfect ranking (0-1 scale)

#### Mathematical Formula

**Discounted Cumulative Gain (DCG):**

$$
\text{DCG@k} = \sum_{i=1}^{k} \frac{\text{relevance}_i}{\log_2(i + 1)}
$$

**Normalized DCG (NDCG):**

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}
$$

Where IDCG = DCG of perfect ranking (all most relevant docs first)

#### Example Calculation

```
Query: "Top fintech startups"

Retrieved (with relevance scores 0-3):
Position 1: Paytm (relevance = 3) → 3 / log₂(2) = 3.0
Position 2: Zomato (relevance = 1) → 1 / log₂(3) = 0.63
Position 3: PhonePe (relevance = 3) → 3 / log₂(4) = 1.5
Position 4: Swiggy (relevance = 2) → 2 / log₂(5) = 0.86

DCG = 3.0 + 0.63 + 1.5 + 0.86 = 5.99

Perfect ranking would be:
Position 1: Paytm (3) → 3.0
Position 2: PhonePe (3) → 1.89
Position 3: Swiggy (2) → 1.0
Position 4: Zomato (1) → 0.43

IDCG = 3.0 + 1.89 + 1.0 + 0.43 = 6.32

NDCG = 5.99 / 6.32 = 0.948 = 94.8%
```

#### Python Code

```python
import math

def dcg_at_k(relevances, k):
    """
    Calculate DCG@k
    
    Args:
        relevances: List of relevance scores (higher = more relevant)
        k: Number of results to consider
    
    Returns:
        DCG score
    """
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        dcg += rel / math.log2(i + 2)  # +2 because i starts at 0
    return dcg

def ndcg_at_k(relevances, k):
    """
    Calculate NDCG@k
    
    Args:
        relevances: List of relevance scores in retrieved order
        k: Number of results to consider
    
    Returns:
        NDCG score (0-1)
    """
    dcg = dcg_at_k(relevances, k)
    
    # Ideal ranking (sorted in descending order)
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal_relevances, k)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg

# Example
retrieved_relevances = [3, 1, 3, 2, 0]  # Actual order
k = 5

ndcg = ndcg_at_k(retrieved_relevances, k)
print(f"NDCG@{k}: {ndcg:.3f}")  # Output: ~0.948
```

#### When to Use

- When **graded relevance** exists (not just relevant/irrelevant)
- When **ranking quality matters** (top positions are critical)
- Search engines, recommendation systems

---

### 6. Cosine Similarity

#### Layman Explanation

**Cosine Similarity** = "How similar are two pieces of text?"

Think of it like:
- Two vectors (arrows) in space
- If they point in same direction → Similar (score = 1)
- If they point opposite directions → Different (score = -1)
- If they're perpendicular → Unrelated (score = 0)

```
    Query Vector
         ↑
         │  θ (angle)
         │ ╱
         │╱
         ├────────→ Document Vector
         
Cosine Similarity = cos(θ)
- θ = 0° → cos(0°) = 1.0 (identical)
- θ = 45° → cos(45°) = 0.707 (similar)
- θ = 90° → cos(90°) = 0.0 (unrelated)
```

#### Mathematical Formula

$$
\text{cosine similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{||\mathbf{A}|| \times ||\mathbf{B}||}
$$

$$
= \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}
$$

#### Example

```
Query embedding: [0.5, 0.8, 0.2]
Doc 1 embedding: [0.6, 0.7, 0.3]
Doc 2 embedding: [0.1, 0.2, 0.9]

Similarity(Query, Doc1):
= (0.5×0.6 + 0.8×0.7 + 0.2×0.3) / (||Query|| × ||Doc1||)
= 0.92 / (0.872 × 0.922)
= 0.97 ← Very similar!

Similarity(Query, Doc2):
= 0.31 / (0.872 × 0.922)
= 0.32 ← Not very similar
```

#### Python Code

```python
import numpy as np

def cosine_similarity(vec_a, vec_b):
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec_a: First vector (list or numpy array)
        vec_b: Second vector (same length as vec_a)
    
    Returns:
        Float between -1 and 1 (usually 0 to 1 for embeddings)
    """
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)
    
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

# Example with Sentence Transformers (actual use in Prometheus)
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

query = "Top fintech startups"
doc1 = "Paytm is a leading fintech company"
doc2 = "Delhi weather is hot in summer"

query_emb = model.encode(query)
doc1_emb = model.encode(doc1)
doc2_emb = model.encode(doc2)

sim1 = cosine_similarity(query_emb, doc1_emb)
sim2 = cosine_similarity(query_emb, doc2_emb)

print(f"Query-Doc1 similarity: {sim1:.3f}")  # High (e.g., 0.85)
print(f"Query-Doc2 similarity: {sim2:.3f}")  # Low (e.g., 0.12)
```

#### When to Use

- **Vector search** in databases like ChromaDB
- **Semantic similarity** matching
- Core metric in Prometheus's RAG pipeline

---

## 📝 Generation Metrics

### 7. Faithfulness (Factual Consistency)

#### Layman Explanation

**Faithfulness** = "Does the answer contain ONLY information from the retrieved documents?"

Think of it like a quiz:
- ✅ Answer based on textbook → Faithful
- ❌ Answer from imagination → Hallucination

#### Example

```
Retrieved Context:
"Swiggy raised $250 crores in Series E funding in 2024 from Naspers."

Generated Answer 1:
"Swiggy raised $250 crores from Naspers in 2024."
→ Faithfulness = 100% ✅

Generated Answer 2:
"Swiggy raised $500 crores from multiple investors in 2023."
→ Faithfulness = 0% ❌ (hallucinated amount and year)
```

#### How to Calculate

**Method 1: Entailment Score (NLI Model)**

Use a Natural Language Inference model:

```python
from transformers import pipeline

nli_model = pipeline("text-classification", 
                    model="microsoft/deberta-large-mnli")

def faithfulness_score(context, answer):
    """
    Calculate faithfulness using NLI model
    
    Args:
        context: Retrieved documents (concatenated)
        answer: Generated answer
    
    Returns:
        Float between 0 and 1
    """
    # Split answer into claims
    claims = answer.split('. ')
    
    faithful_count = 0
    for claim in claims:
        result = nli_model(f"{context} [SEP] {claim}")[0]
        
        # Check if entailed or neutral (not contradicted)
        if result['label'] in ['ENTAILMENT', 'NEUTRAL']:
            faithful_count += 1
    
    return faithful_count / len(claims) if claims else 0.0

# Example
context = "Swiggy raised $250 crores in 2024 from Naspers."
answer = "Swiggy raised $250 crores from Naspers in 2024."

score = faithfulness_score(context, answer)
print(f"Faithfulness: {score:.2f}")
```

**Method 2: Manual Annotation**

Human evaluators check each statement:
1. Break answer into atomic claims
2. Verify each claim against context
3. Calculate percentage of verified claims

#### When to Use

- When **accuracy is critical** (financial, medical, legal)
- Detecting **hallucinations**
- Ensuring **trustworthiness**

---

### 8. Answer Relevance

#### Layman Explanation

**Answer Relevance** = "Does the answer actually address the question?"

Example:
```
Question: "How much funding did Swiggy get?"

Answer 1: "Swiggy received $250 crores in funding."
→ Relevance = High ✅

Answer 2: "Swiggy is a food delivery company founded in 2014."
→ Relevance = Low ❌ (correct but doesn't answer the question)
```

#### How to Calculate

**Method 1: Semantic Similarity**

```python
def answer_relevance(query, answer, model):
    """
    Calculate answer relevance using embeddings
    
    Args:
        query: User's question
        answer: Generated answer
        model: Sentence transformer model
    
    Returns:
        Float between 0 and 1
    """
    query_emb = model.encode(query)
    answer_emb = model.encode(answer)
    
    similarity = cosine_similarity(query_emb, answer_emb)
    return similarity

# Example
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

query = "How much funding did Swiggy get?"
answer = "Swiggy received $250 crores in Series E funding."

score = answer_relevance(query, answer, model)
print(f"Answer Relevance: {score:.3f}")
```

**Method 2: Question Generation (Reverse Check)**

1. Generate questions from the answer
2. Compare generated questions with original query
3. High similarity → High relevance

```python
def question_generation_relevance(query, answer, qa_model):
    """
    Calculate relevance by generating questions from answer
    """
    # Generate question from answer
    generated_q = qa_model.generate_question(answer)
    
    # Compare with original query
    similarity = cosine_similarity(
        embed(query),
        embed(generated_q)
    )
    
    return similarity
```

---

### 9. Context Relevance

#### Layman Explanation

**Context Relevance** = "Were the retrieved documents actually useful for answering the question?"

```
Query: "Top fintech startups in Bangalore"

Retrieved Documents:
1. "Paytm is a fintech startup in Bangalore..." → Relevant ✅
2. "Weather in Bangalore is pleasant..." → Irrelevant ❌
3. "PhonePe, a fintech startup based in Bangalore..." → Relevant ✅

Context Relevance = 2/3 = 67%
```

#### How to Calculate

```python
def context_relevance(query, retrieved_docs, model):
    """
    Calculate average relevance of retrieved documents
    
    Args:
        query: User's question
        retrieved_docs: List of retrieved document texts
        model: Sentence transformer model
    
    Returns:
        Float between 0 and 1
    """
    query_emb = model.encode(query)
    
    relevance_scores = []
    for doc in retrieved_docs:
        doc_emb = model.encode(doc)
        similarity = cosine_similarity(query_emb, doc_emb)
        relevance_scores.append(similarity)
    
    return sum(relevance_scores) / len(relevance_scores)
```

---

### 10. BLEU Score

#### Layman Explanation

**BLEU** = "How similar is the generated text to reference answers?"

Used in machine translation, now adapted for RAG.

Think of it like:
- Comparing your essay to a model answer
- Counting matching words/phrases
- Higher match = Higher score

#### Mathematical Formula

$$
\text{BLEU} = \text{BP} \times \exp\left(\sum_{n=1}^{N} w_n \log p_n\right)
$$

Where:
- $p_n$ = precision for n-grams (1-gram, 2-gram, 3-gram, 4-gram)
- $w_n$ = weights (usually 0.25 for each)
- BP = Brevity Penalty (penalizes short answers)

#### Example

```
Reference: "Swiggy raised 250 crores in funding from Naspers"
Generated: "Swiggy got 250 crores from Naspers"

1-gram matches: "Swiggy", "250", "crores", "from", "Naspers" (5/7)
2-gram matches: "250 crores", "from Naspers" (2/6)
3-gram matches: "250 crores from" (1/5)
4-gram matches: None (0/4)

BLEU = geometric mean of these precisions
```

#### Python Code

```python
from nltk.translate.bleu_score import sentence_bleu

def bleu_score(reference, generated):
    """
    Calculate BLEU score
    
    Args:
        reference: Reference answer (string)
        generated: Generated answer (string)
    
    Returns:
        Float between 0 and 1
    """
    reference_tokens = [reference.split()]
    generated_tokens = generated.split()
    
    score = sentence_bleu(reference_tokens, generated_tokens)
    return score

# Example
ref = "Swiggy raised 250 crores in funding from Naspers"
gen = "Swiggy got 250 crores from Naspers"

score = bleu_score(ref, gen)
print(f"BLEU Score: {score:.3f}")
```

#### Limitations

- Doesn't understand meaning (just word matching)
- Can give high scores to nonsensical text
- Needs reference answers (not always available)

---

### 11. ROUGE Score

#### Layman Explanation

**ROUGE** = "Recall-Oriented Understudy for Gisting Evaluation"

Similar to BLEU but focuses on **recall** (how much of reference is in generated text).

Types:
- **ROUGE-1**: Unigram (single word) overlap
- **ROUGE-2**: Bigram (two-word phrase) overlap
- **ROUGE-L**: Longest common subsequence

#### Example

```
Reference: "Swiggy raised 250 crores from Naspers in 2024"
Generated: "In 2024, Swiggy got 250 crores"

ROUGE-1:
Reference words: {Swiggy, raised, 250, crores, from, Naspers, in, 2024}
Generated words: {In, 2024, Swiggy, got, 250, crores}
Overlap: {Swiggy, 250, crores, in, 2024} = 5 words

Recall = 5/8 = 0.625
Precision = 5/6 = 0.833
F1 = 2 × (0.625 × 0.833) / (0.625 + 0.833) = 0.714
```

#### Python Code

```python
from rouge_score import rouge_scorer

def rouge_scores(reference, generated):
    """
    Calculate ROUGE scores
    
    Args:
        reference: Reference answer
        generated: Generated answer
    
    Returns:
        Dictionary with ROUGE-1, ROUGE-2, ROUGE-L scores
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], 
                                      use_stemmer=True)
    scores = scorer.score(reference, generated)
    
    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure
    }

# Example
ref = "Swiggy raised 250 crores from Naspers in 2024"
gen = "In 2024, Swiggy got 250 crores"

scores = rouge_scores(ref, gen)
for metric, score in scores.items():
    print(f"{metric}: {score:.3f}")
```

---

## 🎯 End-to-End Metrics

### 12. Answer Correctness

#### Layman Explanation

**Answer Correctness** = Combination of:
1. **Factual Correctness**: Are the facts right?
2. **Semantic Similarity**: Is the meaning preserved?

It's like grading an exam:
- ✅ Right facts + Right meaning = 100%
- ⚠️ Right facts + Wrong meaning = 50%
- ❌ Wrong facts = 0%

#### Formula

$$
\text{Answer Correctness} = w_1 \times \text{Factual} + w_2 \times \text{Semantic}
$$

Usually $w_1 = 0.7$, $w_2 = 0.3$ (facts weighted more)

---

### 13. Latency

#### Layman Explanation

**Latency** = "How long does it take to get an answer?"

```
User clicks Send → ⏱️ ... → Answer appears

Time taken = Latency
```

#### Components in RAG

```
Total Latency = Embedding Time + Search Time + LLM Time

Example:
┌─────────────────────────────────────────────────┐
│ Embed Query:     200ms  ██                      │
│ Search ChromaDB: 150ms  █▌                      │
│ Generate Answer: 2000ms ████████████████████    │
│ ─────────────────────────────────────────────── │
│ Total:           2350ms ████████████████████████│
└─────────────────────────────────────────────────┘
```

#### Benchmarks

| Latency | User Experience |
|---------|-----------------|
| < 1 second | ⚡ Instant (excellent) |
| 1-3 seconds | 🟢 Fast (good) |
| 3-5 seconds | 🟡 Acceptable |
| 5-10 seconds | 🟠 Slow (frustrating) |
| > 10 seconds | 🔴 Very slow (unacceptable) |

#### Python Code

```python
import time

def measure_latency(query_function):
    """
    Measure latency of a query
    
    Args:
        query_function: Function to execute
    
    Returns:
        Result and latency in milliseconds
    """
    start = time.time()
    result = query_function()
    end = time.time()
    
    latency_ms = (end - start) * 1000
    return result, latency_ms

# Example
def rag_query(query):
    # Simulated RAG pipeline
    time.sleep(2.35)  # 2350ms
    return "Answer to query"

result, latency = measure_latency(lambda: rag_query("test"))
print(f"Latency: {latency:.0f}ms")
```

---

### 14. Throughput

#### Layman Explanation

**Throughput** = "How many queries can we handle per second?"

```
If 100 users ask questions at the same time,
how many can we answer in 1 second?

High throughput = Can handle many users ✅
Low throughput = Gets slow with many users ❌
```

#### Formula

$$
\text{Throughput} = \frac{\text{Number of Requests}}{\text{Time Period}}
$$

#### Example

```
Handled 500 requests in 10 seconds
Throughput = 500/10 = 50 requests/second
```

---

## 📊 Prometheus-Specific Metrics

### How We Evaluate Prometheus

#### 1. Query Understanding (Multilingual)

```python
def multilingual_accuracy():
    """
    Test if system understands all 8 languages
    """
    test_cases = {
        'en': "Top startups in Bangalore",
        'hi': "बैंगलोर में टॉप स्टार्टअप",
        'ta': "பெங்களூரில் சிறந்த நிறுவனங்கள்",
        # ... other languages
    }
    
    correct = 0
    for lang, query in test_cases.items():
        result = rag_system.query(query, lang)
        if is_about_bangalore_startups(result):
            correct += 1
    
    return correct / len(test_cases)
```

#### 2. Domain-Specific Accuracy

```
Test Categories:
1. Company Names     → 95% accuracy required
2. Funding Amounts   → 98% accuracy (critical!)
3. Investor Names    → 90% accuracy
4. Sectors          → 92% accuracy
5. Cities           → 95% accuracy
6. Years/Dates      → 98% accuracy
```

#### 3. Response Format Quality

```
Good Response:
──────────────
"Here are the top 10 fintech startups in Bangalore:

1. Paytm - ₹250 crores
2. PhonePe - ₹200 crores
...
10. Razorpay - ₹100 crores"

✅ Clear formatting
✅ Correct ₹ symbol
✅ Exactly 10 items (as requested)
✅ Sorted by amount


Bad Response:
─────────────
"some companies got funding paytm phonepe razorpay"

❌ No structure
❌ No amounts
❌ Not sorted
❌ Incomplete
```

---

## 📈 How to Interpret Scores

### Score Ranges

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Precision | > 0.9 | 0.7-0.9 | 0.5-0.7 | < 0.5 |
| Recall | > 0.8 | 0.6-0.8 | 0.4-0.6 | < 0.4 |
| F1 Score | > 0.85 | 0.65-0.85 | 0.45-0.65 | < 0.45 |
| MRR | > 0.8 | 0.6-0.8 | 0.4-0.6 | < 0.4 |
| NDCG | > 0.9 | 0.7-0.9 | 0.5-0.7 | < 0.5 |
| Faithfulness | > 0.95 | 0.85-0.95 | 0.7-0.85 | < 0.7 |
| Latency | < 2s | 2-4s | 4-6s | > 6s |

### Trade-offs

```
┌──────────────────────────────────────────────────────────┐
│              RETRIEVAL TRADE-OFFS                         │
│                                                          │
│  High Precision ←─────────────────→ High Recall          │
│  (Quality)                            (Coverage)         │
│                                                          │
│  Few results,                    Many results,          │
│  all relevant                    some irrelevant        │
│                                                          │
│  Example:                        Example:               │
│  Retrieve top 10                 Retrieve top 100       │
│  Very selective                  Cast wide net          │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Sweet Spot: F1 Score ≈ 0.8 (balance both)              │
└──────────────────────────────────────────────────────────┘
```

---

## 🌍 Real-World Examples

### Example 1: Perfect Retrieval

```
Query: "Swiggy funding amount"

Retrieved (top 5):
1. "Swiggy raised $250 crores..." ✅ Relevance: 3
2. "Swiggy Series E funding details..." ✅ Relevance: 3
3. "Swiggy investors include Naspers..." ✅ Relevance: 2
4. "Swiggy funding history 2014-2024..." ✅ Relevance: 3
5. "Swiggy total funding breakdown..." ✅ Relevance: 3

Metrics:
─────────
Precision@5: 5/5 = 100% ✅
MRR: 1/1 = 1.0 ✅ (first result relevant)
NDCG@5: 0.98 ✅ (nearly perfect ranking)
```

### Example 2: Poor Retrieval

```
Query: "Fintech startups in Bangalore"

Retrieved (top 5):
1. "Weather in Bangalore..." ❌ Relevance: 0
2. "Bangalore IT companies..." ❌ Relevance: 0
3. "Paytm fintech startup Bangalore..." ✅ Relevance: 3
4. "Food delivery in Bangalore..." ❌ Relevance: 0
5. "PhonePe Bangalore office..." ✅ Relevance: 2

Metrics:
─────────
Precision@5: 2/5 = 40% ❌
MRR: 1/3 = 0.33 ❌ (first relevant at position 3)
NDCG@5: 0.42 ❌ (poor ranking)
```

### Example 3: Hallucination Detection

```
Context: "Swiggy raised $250 crores in 2024"

Generated 1: "Swiggy raised $250 crores in 2024"
→ Faithfulness: 100% ✅

Generated 2: "Swiggy raised $500 crores in 2023"
→ Faithfulness: 0% ❌ (hallucinated both amount and year)

Generated 3: "Swiggy, along with Zomato, raised $250 crores"
→ Faithfulness: 50% ❌ (added Zomato which wasn't mentioned)
```

---

## ✅ Best Practices

### 1. Choose the Right Metrics

| Use Case | Primary Metrics | Secondary Metrics |
|----------|----------------|-------------------|
| Search Engine | Precision, NDCG | MRR, Recall |
| Question Answering | Faithfulness, Answer Correctness | Latency |
| Chatbot | Answer Relevance, User Feedback | Coherence |
| E-commerce | Recall, Throughput | Precision |

### 2. Set Realistic Thresholds

```
DON'T aim for 100% on everything!

Better approach:
┌────────────────────────────────────────┐
│ Critical Metrics (must be high):       │
│ • Faithfulness > 95%                   │
│ • Latency < 3s                         │
│                                        │
│ Important Metrics (should be good):    │
│ • Precision > 80%                      │
│ • Answer Relevance > 85%               │
│                                        │
│ Nice to Have:                          │
│ • Recall > 70%                         │
│ • BLEU > 0.6                          │
└────────────────────────────────────────┘
```

### 3. Monitor Over Time

```
Week 1:  Precision = 75%  →  Baseline
Week 2:  Precision = 78%  →  Improving ✅
Week 3:  Precision = 72%  →  Degrading ❌ (investigate!)
Week 4:  Precision = 85%  →  Fixed + improved ✅
```

### 4. Use Multiple Metrics

```
Single metric can be misleading:

System A: Precision = 95%, Recall = 20%
→ High quality but misses too much ❌

System B: Precision = 60%, Recall = 95%
→ Finds everything but quality poor ❌

System C: Precision = 85%, Recall = 80%
→ Balanced! ✅
```

---

## 📚 Summary

### Quick Reference Table

| Metric | What It Measures | Formula | Range | Good Score |
|--------|-----------------|---------|-------|------------|
| **Precision** | Quality of retrieved docs | TP/(TP+FP) | 0-1 | > 0.8 |
| **Recall** | Coverage of retrieval | TP/(TP+FN) | 0-1 | > 0.7 |
| **F1** | Balance of P & R | 2×(P×R)/(P+R) | 0-1 | > 0.75 |
| **MRR** | Ranking quality | Avg(1/rank) | 0-1 | > 0.7 |
| **NDCG** | Graded ranking | DCG/IDCG | 0-1 | > 0.8 |
| **Cosine Sim** | Vector similarity | A·B/(‖A‖‖B‖) | -1 to 1 | > 0.7 |
| **Faithfulness** | No hallucinations | Verified/Total | 0-1 | > 0.95 |
| **Answer Rel** | Answers question | Semantic sim | 0-1 | > 0.85 |
| **Latency** | Response time | Time (ms) | 0-∞ | < 3000ms |

### Key Takeaways

1. **No single metric is perfect** - Use combination
2. **Context matters** - Medical AI needs higher faithfulness than chatbot
3. **Monitor trends** - One-time scores less useful than tracking over time
4. **User feedback** - Sometimes simplest metric (thumbs up/down) most valuable
5. **Balance trade-offs** - Perfect precision might sacrifice recall

---

*This guide covers the main evaluation metrics for RAG systems. For Prometheus specifically, focus on: Precision, Faithfulness, Answer Relevance, and Latency.*
