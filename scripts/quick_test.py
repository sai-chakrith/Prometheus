"""Quick test to validate Prometheus RAG responses"""
import requests
import time

BASE_URL = "http://localhost:8000"

test_queries = [
    # English
    {"query": "2024 EdTech funding", "lang": "en", "name": "English - EdTech 2024"},
    {"query": "Fintech companies in Pune", "lang": "en", "name": "English - Pune Fintech"},
    
    # Hindi
    {"query": "2024 में एडटेक की फंडिंग दिखाओ", "lang": "hi", "name": "Hindi - EdTech 2024"},
    {"query": "बैंगलोर में शीर्ष स्टार्टअप", "lang": "hi", "name": "Hindi - Bangalore"},
    
    # Telugu
    {"query": "2024 లో ఫిన్టెక్ కంపెనీలు", "lang": "te", "name": "Telugu - Fintech 2024"},
    {"query": "బెంగళూరు లో టాప్ స్టార్టప్స్", "lang": "te", "name": "Telugu - Bangalore"},
    
    # Tamil  
    {"query": "2024 இல் எட்டெக் நிதி காட்டு", "lang": "ta", "name": "Tamil - EdTech 2024"},
]

print("\n🚀 PROMETHEUS QUICK TEST\n" + "="*60)

passed = 0
failed = 0

for test in test_queries:
    print(f"\n📝 {test['name']}")
    print(f"   Query: {test['query']}")
    
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/rag",
            json={"query": test["query"], "language": test["lang"]},
            timeout=30
        )
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            
            # Check if response is valid
            if len(answer) > 50 and "₹" in answer:
                print(f"   ✅ PASS ({duration:.2f}s)")
                print(f"   Preview: {answer[:150]}...")
                passed += 1
            else:
                print(f"   ❌ FAIL - Short or invalid response ({duration:.2f}s)")
                print(f"   Answer: {answer}")
                failed += 1
        else:
            print(f"   ❌ FAIL - HTTP {response.status_code}")
            failed += 1
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed")
print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%\n")
