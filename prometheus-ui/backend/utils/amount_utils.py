"""
Utility functions for amount parsing and formatting
"""
import re

def parse_amount_to_numeric(amount_str):
    """Convert amount string like '₹0.02 L' or '₹5 Cr' to numeric value in rupees"""
    try:
        if not amount_str or amount_str == 'Unknown':
            return 0.0
        
        amount_str = str(amount_str).strip()
        # Extract numeric part
        num_match = re.search(r'[\d,]+\.?\d*', amount_str)
        if not num_match:
            return 0.0
        
        num = float(num_match.group().replace(',', ''))
        
        # Check for multiplier
        if 'Cr' in amount_str:
            return num * 10_000_000  # 1 Crore = 10 million
        elif 'L' in amount_str:
            return num * 100_000  # 1 Lakh = 100,000
        elif 'K' in amount_str:
            return num * 1_000
        elif 'M' in amount_str:
            return num * 1_000_000
        else:
            return num
    except:
        return 0.0

def format_amount(amount: str) -> str:
    """Format amount in readable form"""
    try:
        # Extract numeric value
        num_match = re.search(r'[\d,\.]+', str(amount))
        if num_match:
            num_str = num_match.group().replace(',', '')
            num = float(num_str)
            
            if 'M' in str(amount) or num >= 1_000_000:
                return f"${num/1_000_000:.1f}M"
            elif 'K' in str(amount) or num >= 1_000:
                return f"${num/1_000:.0f}K"
        return str(amount)
    except:
        return str(amount)
