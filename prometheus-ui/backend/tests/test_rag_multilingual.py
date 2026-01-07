# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for Prometheus LLM & RAG Model
Tests across multiple languages: English, Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali
"""

import requests
import json
import time
import re
import sys
import io
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"

class TestStatus(Enum):
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    WARNING = "⚠️ WARNING"

@dataclass
class TestResult:
    test_name: str
    language: str
    query: str
    status: TestStatus
    expected: str
    actual: str
    response_time: float
    details: str = ""

class PrometheusRAGTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.base_url = BASE_URL
        
    def query_rag(self, query: str, language: str = "en") -> Tuple[Dict, float]:
        """Send query to RAG endpoint and measure response time"""
        start_time = time.time()
        try:
            # Ensure proper UTF-8 encoding for multilingual queries
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            payload = json.dumps({"query": query, "language": language}, ensure_ascii=False).encode('utf-8')
            
            response = requests.post(
                f"{self.base_url}/api/rag",
                data=payload,
                headers=headers,
                timeout=120
            )
            elapsed = time.time() - start_time
            if response.status_code == 200:
                return response.json(), elapsed
            else:
                return {"error": f"HTTP {response.status_code}", "answer": "", "sources": []}, elapsed
        except Exception as e:
            return {"error": str(e), "answer": "", "sources": []}, time.time() - start_time

    def validate_response(self, response: Dict, validators: Dict) -> Tuple[bool, str]:
        """Validate response against expected criteria"""
        issues = []
        
        # Check if response has answer
        if not response.get("answer"):
            issues.append("No answer in response")
            return False, "; ".join(issues)
        
        answer = response.get("answer", "").lower()
        sources = response.get("sources", [])
        
        # Check for expected sector
        if "expected_sector" in validators:
            sector = validators["expected_sector"].lower()
            sector_found = any(sector in str(s.get("sector", "")).lower() for s in sources)
            if not sector_found and sector not in answer:
                issues.append(f"Expected sector '{validators['expected_sector']}' not found")
        
        # Check for expected company
        if "expected_company" in validators:
            company = validators["expected_company"].lower()
            company_found = any(company in str(s.get("company", "")).lower() for s in sources)
            if not company_found and company not in answer:
                issues.append(f"Expected company '{validators['expected_company']}' not found")
        
        # Check for expected city
        if "expected_city" in validators:
            city = validators["expected_city"].lower()
            city_found = any(city in str(s.get("city", "")).lower() for s in sources)
            if not city_found and city not in answer:
                issues.append(f"Expected city '{validators['expected_city']}' not found")
        
        # Check minimum sources
        if "min_sources" in validators:
            if len(sources) < validators["min_sources"]:
                issues.append(f"Expected at least {validators['min_sources']} sources, got {len(sources)}")
        
        # Check for funding amount pattern
        if "has_amount" in validators and validators["has_amount"]:
            amount_pattern = r'₹[\d,\.]+\s*(Cr|L|cr|l)|[\d,\.]+\s*(Cr|L|cr|l|crore|lakh)'
            if not re.search(amount_pattern, response.get("answer", ""), re.IGNORECASE):
                issues.append("No funding amount found in response")
        
        # Check for year
        if "expected_year" in validators:
            year = str(validators["expected_year"])
            year_found = any(year in str(s.get("year", "")) for s in sources)
            if not year_found and year not in answer:
                issues.append(f"Expected year '{year}' not found")
        
        # Check sorting (highest funding)
        if "check_highest_first" in validators and validators["check_highest_first"]:
            if len(sources) >= 2:
                # Parse amounts and check order
                amounts = []
                for s in sources[:5]:
                    amt_str = s.get("amount", "0")
                    match = re.search(r'[\d,\.]+', str(amt_str))
                    if match:
                        amt = float(match.group().replace(',', ''))
                        if 'Cr' in str(amt_str):
                            amt *= 10000000
                        elif 'L' in str(amt_str):
                            amt *= 100000
                        amounts.append(amt)
                if amounts and amounts != sorted(amounts, reverse=True):
                    issues.append("Results not sorted by highest funding")
        
        # Check sorting (lowest funding)
        if "check_lowest_first" in validators and validators["check_lowest_first"]:
            if len(sources) >= 2:
                amounts = []
                for s in sources[:5]:
                    amt_str = s.get("amount", "0")
                    match = re.search(r'[\d,\.]+', str(amt_str))
                    if match:
                        amt = float(match.group().replace(',', ''))
                        if 'Cr' in str(amt_str):
                            amt *= 10000000
                        elif 'L' in str(amt_str):
                            amt *= 100000
                        amounts.append(amt)
                if amounts and amounts != sorted(amounts):
                    issues.append("Results not sorted by lowest funding")
        
        # Check for no irrelevant sectors
        if "exclude_sectors" in validators:
            for s in sources:
                src_sector = str(s.get("sector", "")).lower()
                for exclude in validators["exclude_sectors"]:
                    if exclude.lower() in src_sector:
                        issues.append(f"Irrelevant sector '{exclude}' found in results")
                        break
        
        # Check response is not error message
        if "error" in response and response["error"]:
            issues.append(f"Error in response: {response['error']}")
        
        return len(issues) == 0, "; ".join(issues) if issues else "All validations passed"

    def run_test(self, test_name: str, language: str, query: str, 
                 validators: Dict, expected_description: str) -> TestResult:
        """Run a single test case"""
        print(f"\n🔍 Testing: {test_name}")
        print(f"   Query ({language}): {query}")
        
        response, elapsed = self.query_rag(query, language)
        passed, details = self.validate_response(response, validators)
        
        status = TestStatus.PASSED if passed else TestStatus.FAILED
        
        # Check for warnings (slow response)
        if elapsed > 30:
            if status == TestStatus.PASSED:
                status = TestStatus.WARNING
                details += f"; Slow response ({elapsed:.1f}s)"
        
        result = TestResult(
            test_name=test_name,
            language=language,
            query=query,
            status=status,
            expected=expected_description,
            actual=response.get("answer", "")[:200] + "..." if len(response.get("answer", "")) > 200 else response.get("answer", ""),
            response_time=elapsed,
            details=details
        )
        
        self.results.append(result)
        print(f"   {status.value} ({elapsed:.2f}s)")
        if details and status != TestStatus.PASSED:
            print(f"   Details: {details}")
        
        return result

    # ==================== ENGLISH TEST CASES ====================
    
    def test_english_sector_query(self):
        """Test basic sector queries in English"""
        tests = [
            {
                "name": "EN_SECTOR_01: Fintech sector query",
                "query": "Show me fintech companies",
                "validators": {"expected_sector": "Fintech", "min_sources": 3},
                "expected": "Returns fintech companies with funding details"
            },
            {
                "name": "EN_SECTOR_02: Healthtech sector query",
                "query": "List healthcare startups in India",
                "validators": {"expected_sector": "Healthtech", "min_sources": 3},
                "expected": "Returns healthtech/healthcare companies"
            },
            {
                "name": "EN_SECTOR_03: Edtech sector query",
                "query": "What are the top edtech companies?",
                "validators": {"expected_sector": "Edtech", "min_sources": 3},
                "expected": "Returns edtech companies"
            },
            {
                "name": "EN_SECTOR_04: E-commerce sector query",
                "query": "Show ecommerce startups",
                "validators": {"expected_sector": "E-Commerce", "min_sources": 3},
                "expected": "Returns e-commerce companies"
            },
            {
                "name": "EN_SECTOR_05: SaaS sector query",
                "query": "List SaaS companies with funding",
                "validators": {"expected_sector": "SaaS", "min_sources": 3},
                "expected": "Returns SaaS companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    def test_english_city_queries(self):
        """Test city-based queries in English"""
        tests = [
            {
                "name": "EN_CITY_01: Bangalore startups",
                "query": "Show startups in Bangalore",
                "validators": {"expected_city": "Bangalore", "min_sources": 3},
                "expected": "Returns companies based in Bangalore"
            },
            {
                "name": "EN_CITY_02: Mumbai startups",
                "query": "List companies in Mumbai",
                "validators": {"expected_city": "Mumbai", "min_sources": 3},
                "expected": "Returns companies based in Mumbai"
            },
            {
                "name": "EN_CITY_03: Hyderabad tech companies",
                "query": "Tech startups in Hyderabad",
                "validators": {"expected_city": "Hyderabad", "min_sources": 2},
                "expected": "Returns companies based in Hyderabad"
            },
            {
                "name": "EN_CITY_04: Chennai startups",
                "query": "Show Chennai based startups",
                "validators": {"expected_city": "Chennai", "min_sources": 2},
                "expected": "Returns companies based in Chennai"
            },
            {
                "name": "EN_CITY_05: Delhi NCR startups",
                "query": "Startups in Delhi",
                "validators": {"expected_city": "Delhi", "min_sources": 2},
                "expected": "Returns companies based in Delhi/NCR"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    def test_english_sorting_queries(self):
        """Test sorting functionality"""
        tests = [
            {
                "name": "EN_SORT_01: Highest funding",
                "query": "Rank companies with highest funding",
                "validators": {"check_highest_first": True, "has_amount": True, "min_sources": 5},
                "expected": "Returns companies sorted by highest funding first"
            },
            {
                "name": "EN_SORT_02: Lowest funding",
                "query": "Show startups with lowest funding",
                "validators": {"check_lowest_first": True, "has_amount": True, "min_sources": 3},
                "expected": "Returns companies sorted by lowest funding first"
            },
            {
                "name": "EN_SORT_03: Top funded fintech",
                "query": "Top 5 most funded fintech companies",
                "validators": {"expected_sector": "Fintech", "check_highest_first": True, "has_amount": True},
                "expected": "Returns top funded fintech companies"
            },
            {
                "name": "EN_SORT_04: Latest funding rounds",
                "query": "Show latest funding rounds in 2024",
                "validators": {"expected_year": "2024", "min_sources": 3},
                "expected": "Returns recent funding rounds from 2024"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    def test_english_company_queries(self):
        """Test company-specific queries"""
        tests = [
            {
                "name": "EN_COMPANY_01: Specific company lookup",
                "query": "Tell me about M2P Fintech",
                "validators": {"expected_company": "M2P Fintech", "has_amount": True},
                "expected": "Returns M2P Fintech funding details"
            },
            {
                "name": "EN_COMPANY_02: Company comparison",
                "query": "Compare Razorpay and Paytm funding",
                "validators": {"min_sources": 2, "has_amount": True},
                "expected": "Returns comparison of both companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    def test_english_sector_comparison(self):
        """Test sector comparison queries"""
        tests = [
            {
                "name": "EN_COMPARE_01: Fintech vs Healthcare",
                "query": "Compare fintech and healthcare sectors",
                "validators": {"min_sources": 4},
                "expected": "Returns comparison of both sectors"
            },
            {
                "name": "EN_COMPARE_02: Edtech vs SaaS",
                "query": "Compare edtech with saas funding",
                "validators": {"min_sources": 4},
                "expected": "Returns comparison of both sectors"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    def test_english_year_queries(self):
        """Test year-based filtering"""
        tests = [
            {
                "name": "EN_YEAR_01: 2023 funding",
                "query": "Show funding rounds in 2023",
                "validators": {"expected_year": "2023", "min_sources": 3, "has_amount": True},
                "expected": "Returns 2023 funding rounds"
            },
            {
                "name": "EN_YEAR_02: 2024 startups",
                "query": "Which companies raised funding in 2024?",
                "validators": {"expected_year": "2024", "min_sources": 3},
                "expected": "Returns 2024 funding rounds"
            },
            {
                "name": "EN_YEAR_03: Historical 2020 data",
                "query": "Funding rounds from 2020",
                "validators": {"expected_year": "2020", "min_sources": 2},
                "expected": "Returns 2020 funding rounds"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    # ==================== HINDI TEST CASES ====================
    
    def test_hindi_sector_queries(self):
        """Test Hindi language sector queries"""
        tests = [
            {
                "name": "HI_SECTOR_01: Fintech in Hindi",
                "query": "फिनटेक कंपनियां दिखाओ",
                "validators": {"expected_sector": "Fintech", "min_sources": 3},
                "expected": "Returns fintech companies for Hindi query"
            },
            {
                "name": "HI_SECTOR_02: Healthcare in Hindi",
                "query": "स्वास्थ्य सेवा स्टार्टअप",
                "validators": {"expected_sector": "Healthtech", "min_sources": 2},
                "expected": "Returns healthtech companies for Hindi query"
            },
            {
                "name": "HI_SECTOR_03: Education in Hindi",
                "query": "शिक्षा क्षेत्र की कंपनियां",
                "validators": {"expected_sector": "Edtech", "min_sources": 2},
                "expected": "Returns edtech companies for Hindi query"
            },
            {
                "name": "HI_SECTOR_04: Technology in Hindi",
                "query": "टेक्नोलॉजी स्टार्टअप्स",
                "validators": {"min_sources": 3},
                "expected": "Returns technology companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "hi", test["query"], 
                         test["validators"], test["expected"])

    def test_hindi_city_queries(self):
        """Test Hindi city-based queries"""
        tests = [
            {
                "name": "HI_CITY_01: Bangalore in Hindi",
                "query": "बैंगलोर की कंपनियां",
                "validators": {"expected_city": "Bangalore", "min_sources": 2},
                "expected": "Returns Bangalore companies for Hindi query"
            },
            {
                "name": "HI_CITY_02: Mumbai in Hindi",
                "query": "मुंबई के स्टार्टअप",
                "validators": {"expected_city": "Mumbai", "min_sources": 2},
                "expected": "Returns Mumbai companies for Hindi query"
            },
            {
                "name": "HI_CITY_03: Delhi in Hindi",
                "query": "दिल्ली में फंडिंग",
                "validators": {"expected_city": "Delhi", "min_sources": 2},
                "expected": "Returns Delhi companies for Hindi query"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "hi", test["query"], 
                         test["validators"], test["expected"])

    def test_hindi_funding_queries(self):
        """Test Hindi funding-related queries"""
        tests = [
            {
                "name": "HI_FUND_01: Highest funding Hindi",
                "query": "सबसे ज्यादा फंडिंग वाली कंपनी",
                "validators": {"has_amount": True, "min_sources": 3},
                "expected": "Returns highest funded companies"
            },
            {
                "name": "HI_FUND_02: Recent funding Hindi",
                "query": "हाल की फंडिंग",
                "validators": {"has_amount": True, "min_sources": 3},
                "expected": "Returns recent funding rounds"
            },
            {
                "name": "HI_FUND_03: Crore funding Hindi",
                "query": "सौ करोड़ से ज्यादा फंडिंग",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns companies with 100+ Cr funding"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "hi", test["query"], 
                         test["validators"], test["expected"])

    # ==================== TAMIL TEST CASES ====================
    
    def test_tamil_queries(self):
        """Test Tamil language queries"""
        tests = [
            {
                "name": "TA_SECTOR_01: Fintech in Tamil",
                "query": "ஃபின்டெக் நிறுவனங்கள்",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Returns fintech companies for Tamil query"
            },
            {
                "name": "TA_CITY_01: Chennai in Tamil",
                "query": "சென்னை நிறுவனங்கள்",
                "validators": {"expected_city": "Chennai", "min_sources": 2},
                "expected": "Returns Chennai companies for Tamil query"
            },
            {
                "name": "TA_FUND_01: Funding in Tamil",
                "query": "அதிக நிதி பெற்ற நிறுவனங்கள்",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns highly funded companies"
            },
            {
                "name": "TA_SECTOR_02: Technology Tamil",
                "query": "தொழில்நுட்ப துவக்க நிறுவனங்கள்",
                "validators": {"min_sources": 2},
                "expected": "Returns tech startups"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "ta", test["query"], 
                         test["validators"], test["expected"])

    # ==================== TELUGU TEST CASES ====================
    
    def test_telugu_queries(self):
        """Test Telugu language queries"""
        tests = [
            {
                "name": "TE_SECTOR_01: Fintech in Telugu",
                "query": "ఫిన్‌టెక్ కంపెనీలు",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Returns fintech companies for Telugu query"
            },
            {
                "name": "TE_CITY_01: Hyderabad in Telugu",
                "query": "హైదరాబాద్ స్టార్టప్‌లు",
                "validators": {"expected_city": "Hyderabad", "min_sources": 2},
                "expected": "Returns Hyderabad companies for Telugu query"
            },
            {
                "name": "TE_FUND_01: Funding in Telugu",
                "query": "అత్యధిక నిధులు పొందిన కంపెనీలు",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns highly funded companies"
            },
            {
                "name": "TE_SECTOR_02: Healthcare Telugu",
                "query": "ఆరోగ్య సంరక్షణ స్టార్టప్‌లు",
                "validators": {"expected_sector": "Healthtech", "min_sources": 2},
                "expected": "Returns healthtech companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "te", test["query"], 
                         test["validators"], test["expected"])

    # ==================== KANNADA TEST CASES ====================
    
    def test_kannada_queries(self):
        """Test Kannada language queries"""
        tests = [
            {
                "name": "KN_SECTOR_01: Fintech in Kannada",
                "query": "ಫಿನ್‌ಟೆಕ್ ಕಂಪನಿಗಳು",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Returns fintech companies for Kannada query"
            },
            {
                "name": "KN_CITY_01: Bangalore in Kannada",
                "query": "ಬೆಂಗಳೂರು ಸ್ಟಾರ್ಟ್‌ಅಪ್‌ಗಳು",
                "validators": {"expected_city": "Bangalore", "min_sources": 2},
                "expected": "Returns Bangalore companies for Kannada query"
            },
            {
                "name": "KN_FUND_01: Funding in Kannada",
                "query": "ಹೆಚ್ಚಿನ ಹಣಕಾಸು ಪಡೆದ ಕಂಪನಿಗಳು",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns highly funded companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "kn", test["query"], 
                         test["validators"], test["expected"])

    # ==================== MALAYALAM TEST CASES ====================
    
    def test_malayalam_queries(self):
        """Test Malayalam language queries"""
        tests = [
            {
                "name": "ML_SECTOR_01: Fintech in Malayalam",
                "query": "ഫിൻടെക് കമ്പനികൾ",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Returns fintech companies for Malayalam query"
            },
            {
                "name": "ML_CITY_01: Kerala startups",
                "query": "കേരള സ്റ്റാർട്ടപ്പുകൾ",
                "validators": {"min_sources": 2},
                "expected": "Returns Kerala/Kochi companies"
            },
            {
                "name": "ML_FUND_01: Funding in Malayalam",
                "query": "ഏറ്റവും കൂടുതൽ ഫണ്ടിംഗ്",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns highly funded companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "ml", test["query"], 
                         test["validators"], test["expected"])

    # ==================== BENGALI TEST CASES ====================
    
    def test_bengali_queries(self):
        """Test Bengali language queries"""
        tests = [
            {
                "name": "BN_SECTOR_01: Fintech in Bengali",
                "query": "ফিনটেক কোম্পানি",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Returns fintech companies for Bengali query"
            },
            {
                "name": "BN_CITY_01: Kolkata startups",
                "query": "কলকাতা স্টার্টআপ",
                "validators": {"min_sources": 1},
                "expected": "Returns Kolkata companies"
            },
            {
                "name": "BN_FUND_01: Funding in Bengali",
                "query": "সর্বোচ্চ অর্থায়ন",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns highly funded companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "bn", test["query"], 
                         test["validators"], test["expected"])

    # ==================== MIXED LANGUAGE TEST CASES ====================
    
    def test_mixed_language_queries(self):
        """Test mixed language (Hinglish, code-mixed) queries"""
        tests = [
            {
                "name": "MIX_01: Hinglish fintech",
                "query": "Fintech ki companies dikhao",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Returns fintech companies for Hinglish query"
            },
            {
                "name": "MIX_02: Hinglish city",
                "query": "Bangalore mein startups",
                "validators": {"expected_city": "Bangalore", "min_sources": 2},
                "expected": "Returns Bangalore companies for Hinglish query"
            },
            {
                "name": "MIX_03: English-Hindi funding",
                "query": "Sabse zyada funding wali company",
                "validators": {"has_amount": True, "min_sources": 2},
                "expected": "Returns highly funded companies"
            },
            {
                "name": "MIX_04: Transliterated Hindi",
                "query": "healthtech ki jaankari",
                "validators": {"expected_sector": "Healthtech", "min_sources": 2},
                "expected": "Returns healthtech companies"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "hi", test["query"], 
                         test["validators"], test["expected"])

    # ==================== EDGE CASE TEST CASES ====================
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        tests = [
            {
                "name": "EDGE_01: Minimal valid query",
                "query": "startups",  # Minimal meaningful query
                "validators": {"min_sources": 1},
                "expected": "Should return results for minimal query"
            },
            {
                "name": "EDGE_02: Long query with fintech",
                "query": "fintech companies in Bangalore Mumbai Delhi Chennai Hyderabad with funding details",
                "validators": {"expected_sector": "Fintech", "min_sources": 2},
                "expected": "Should handle long query and return fintech results"
            },
            {
                "name": "EDGE_03: Special characters",
                "query": "funding @#$% companies!!!",
                "validators": {"min_sources": 1},
                "expected": "Should handle special characters"
            },
            {
                "name": "EDGE_04: Unavailable sector",
                "query": "Show me FMCG companies",
                "validators": {},
                "expected": "Should indicate sector is not available"
            },
            {
                "name": "EDGE_05: Numeric query",
                "query": "100 crore funding",
                "validators": {"has_amount": True, "min_sources": 1},
                "expected": "Should understand funding amount query"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    # ==================== ADVANCED QUERY TEST CASES ====================
    
    def test_advanced_queries(self):
        """Test complex and advanced queries"""
        tests = [
            {
                "name": "ADV_01: Multi-filter query",
                "query": "Fintech companies in Bangalore in 2023",
                "validators": {"expected_sector": "Fintech", "expected_city": "Bangalore", "expected_year": "2023"},
                "expected": "Returns fintech companies in Bangalore from 2023"
            },
            {
                "name": "ADV_02: Investor query",
                "query": "Companies funded by Sequoia",
                "validators": {"min_sources": 1},
                "expected": "Returns companies with Sequoia as investor"
            },
            {
                "name": "ADV_03: Series query",
                "query": "Series A funding rounds",
                "validators": {"min_sources": 2, "has_amount": True},
                "expected": "Returns Series A funding information"
            },
            {
                "name": "ADV_04: Trend query",
                "query": "Funding trends in edtech sector",
                "validators": {"expected_sector": "Edtech", "min_sources": 2},
                "expected": "Returns edtech funding information"
            },
        ]
        
        for test in tests:
            self.run_test(test["name"], "en", test["query"], 
                         test["validators"], test["expected"])

    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 80)
        print("🚀 PROMETHEUS RAG MULTILINGUAL TEST SUITE")
        print("=" * 80)
        
        # Check server health first
        try:
            health = requests.get(f"{self.base_url}/health", timeout=10)
            if health.status_code == 200:
                print("✅ Server is healthy")
            else:
                print("❌ Server health check failed")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return
        
        # Run all test categories
        test_methods = [
            ("English Sector Queries", self.test_english_sector_query),
            ("English City Queries", self.test_english_city_queries),
            ("English Sorting Queries", self.test_english_sorting_queries),
            ("English Company Queries", self.test_english_company_queries),
            ("English Sector Comparison", self.test_english_sector_comparison),
            ("English Year Queries", self.test_english_year_queries),
            ("Hindi Sector Queries", self.test_hindi_sector_queries),
            ("Hindi City Queries", self.test_hindi_city_queries),
            ("Hindi Funding Queries", self.test_hindi_funding_queries),
            ("Tamil Queries", self.test_tamil_queries),
            ("Telugu Queries", self.test_telugu_queries),
            ("Kannada Queries", self.test_kannada_queries),
            ("Malayalam Queries", self.test_malayalam_queries),
            ("Bengali Queries", self.test_bengali_queries),
            ("Mixed Language Queries", self.test_mixed_language_queries),
            ("Edge Cases", self.test_edge_cases),
            ("Advanced Queries", self.test_advanced_queries),
        ]
        
        for category_name, test_method in test_methods:
            print(f"\n{'='*60}")
            print(f"📋 {category_name}")
            print("="*60)
            test_method()
        
        self.print_summary()
        self.generate_recommendations()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        total = len(self.results)
        
        print(f"\n✅ Passed:   {passed}/{total} ({100*passed/total:.1f}%)")
        print(f"❌ Failed:   {failed}/{total} ({100*failed/total:.1f}%)")
        print(f"⚠️  Warnings: {warnings}/{total} ({100*warnings/total:.1f}%)")
        
        avg_time = sum(r.response_time for r in self.results) / total if total > 0 else 0
        print(f"\n⏱️  Average response time: {avg_time:.2f}s")
        
        # Group by language
        print("\n📈 Results by Language:")
        languages = {}
        for r in self.results:
            if r.language not in languages:
                languages[r.language] = {"passed": 0, "failed": 0, "total": 0}
            languages[r.language]["total"] += 1
            if r.status == TestStatus.PASSED:
                languages[r.language]["passed"] += 1
            elif r.status == TestStatus.FAILED:
                languages[r.language]["failed"] += 1
        
        for lang, stats in sorted(languages.items()):
            pass_rate = 100 * stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            print(f"   {lang}: {stats['passed']}/{stats['total']} passed ({pass_rate:.0f}%)")
        
        # List failed tests
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            print("-" * 60)
            for r in self.results:
                if r.status == TestStatus.FAILED:
                    print(f"\n🔴 {r.test_name}")
                    print(f"   Query: {r.query}")
                    print(f"   Issue: {r.details}")

    def generate_recommendations(self):
        """Generate recommendations based on test failures"""
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS FOR IMPROVEMENT")
        print("=" * 80)
        
        recommendations = []
        
        # Analyze failures by category
        sector_failures = [r for r in self.results if r.status == TestStatus.FAILED and "SECTOR" in r.test_name]
        city_failures = [r for r in self.results if r.status == TestStatus.FAILED and "CITY" in r.test_name]
        sort_failures = [r for r in self.results if r.status == TestStatus.FAILED and "SORT" in r.test_name]
        hindi_failures = [r for r in self.results if r.status == TestStatus.FAILED and r.language == "hi"]
        tamil_failures = [r for r in self.results if r.status == TestStatus.FAILED and r.language == "ta"]
        telugu_failures = [r for r in self.results if r.status == TestStatus.FAILED and r.language == "te"]
        kannada_failures = [r for r in self.results if r.status == TestStatus.FAILED and r.language == "kn"]
        malayalam_failures = [r for r in self.results if r.status == TestStatus.FAILED and r.language == "ml"]
        bengali_failures = [r for r in self.results if r.status == TestStatus.FAILED and r.language == "bn"]
        
        if sector_failures:
            recommendations.append({
                "issue": "Sector Detection Issues",
                "count": len(sector_failures),
                "fix": """
1. Add more sector aliases in SECTOR_ALIASES dictionary
2. Improve sector term detection in query parsing
3. Add fuzzy matching for sector names
Code change in main.py:
    SECTOR_ALIASES = {
        'healthcare': 'Healthtech',
        'health': 'Healthtech',
        'medical': 'Healthtech',
        'hospital': 'Healthtech',
        # Add more aliases...
    }
"""
            })
        
        if city_failures:
            recommendations.append({
                "issue": "City Detection Issues",
                "count": len(city_failures),
                "fix": """
1. Expand CITY_MAPPING with more variations
2. Add transliterated city names
3. Handle state-level queries
Code change in main.py:
    CITY_MAPPING = {
        'bangalore': ['bangalore', 'bengaluru', 'blr'],
        'mumbai': ['mumbai', 'bombay'],
        # Add regional language names...
    }
"""
            })
        
        if sort_failures:
            recommendations.append({
                "issue": "Sorting Issues",
                "count": len(sort_failures),
                "fix": """
1. Verify parse_amount_to_numeric handles all formats
2. Check amount_numeric field is properly set
3. Ensure sorting keys are correct
Debug: Add logging in sorting section to trace values
"""
            })
        
        if hindi_failures:
            recommendations.append({
                "issue": "Hindi Language Processing Issues",
                "count": len(hindi_failures),
                "fix": """
1. Add Hindi sector keywords:
   HINDI_SECTORS = {
       'फिनटेक': 'Fintech',
       'स्वास्थ्य': 'Healthtech',
       'शिक्षा': 'Edtech',
       'ई-कॉमर्स': 'E-Commerce'
   }
2. Add Hindi city names to CITY_MAPPING
3. Improve query translation before processing
"""
            })
        
        if tamil_failures:
            recommendations.append({
                "issue": "Tamil Language Processing Issues", 
                "count": len(tamil_failures),
                "fix": """
1. Add Tamil sector keywords translation
2. Add Tamil city names (சென்னை -> Chennai)
3. Consider using translation service for Tamil queries
"""
            })
        
        if telugu_failures:
            recommendations.append({
                "issue": "Telugu Language Processing Issues",
                "count": len(telugu_failures),
                "fix": """
1. Add Telugu sector keywords translation
2. Add Telugu city names (హైదరాబాద్ -> Hyderabad)
3. Improve Telugu query preprocessing
"""
            })
        
        if kannada_failures:
            recommendations.append({
                "issue": "Kannada Language Processing Issues",
                "count": len(kannada_failures),
                "fix": """
1. Add Kannada sector keywords
2. Add Kannada city names (ಬೆಂಗಳೂರು -> Bangalore)
3. Enable translation for Kannada queries
"""
            })
        
        if malayalam_failures:
            recommendations.append({
                "issue": "Malayalam Language Processing Issues",
                "count": len(malayalam_failures),
                "fix": """
1. Add Malayalam sector keywords
2. Add Kerala cities mapping
3. Enable translation preprocessing
"""
            })
        
        if bengali_failures:
            recommendations.append({
                "issue": "Bengali Language Processing Issues",
                "count": len(bengali_failures),
                "fix": """
1. Add Bengali sector keywords (ফিনটেক -> Fintech)
2. Add Bengali city names (কলকাতা -> Kolkata)
3. Improve query translation for Bengali
"""
            })
        
        # Check for slow responses
        slow_tests = [r for r in self.results if r.response_time > 20]
        if slow_tests:
            recommendations.append({
                "issue": "Performance Issues",
                "count": len(slow_tests),
                "fix": """
1. Enable response caching for common queries
2. Optimize ChromaDB query parameters
3. Consider batch processing for similar queries
4. Reduce number of results retrieved initially
"""
            })
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['issue']} ({rec['count']} failures)")
            print("-" * 40)
            print(rec['fix'])
        
        if not recommendations:
            print("\n🎉 All tests passed! No recommendations needed.")
        
        return recommendations


def main():
    """Main entry point"""
    tester = PrometheusRAGTester()
    tester.run_all_tests()
    
    # Save results to JSON
    results_data = []
    for r in tester.results:
        results_data.append({
            "test_name": r.test_name,
            "language": r.language,
            "query": r.query,
            "status": r.status.value,
            "expected": r.expected,
            "response_time": r.response_time,
            "details": r.details
        })
    
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Results saved to test_results.json")


if __name__ == "__main__":
    main()
