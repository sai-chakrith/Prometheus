import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


# State to major cities mapping
STATE_TO_CITIES = {
    'karnataka': ['bangalore', 'bengaluru'],
    'maharashtra': ['mumbai', 'pune'],
    'delhi': ['new delhi', 'delhi'],
    'haryana': ['gurgaon', 'gurugram', 'noida'],
    'telangana': ['hyderabad'],
    'tamil nadu': ['chennai'],
    'gujarat': ['ahmedabad'],
    'rajasthan': ['jaipur'],
    'west bengal': ['kolkata', 'calcutta'],
}

# Sector keywords to standardized sector partial matches
SECTOR_KEYWORDS = {
    'fintech': ['payment', 'financial', 'wallet', 'lending', 'insurance', 'banking', 'finance'],
    'edtech': ['education', 'learning', 'online education', 'e-learning'],
    'foodtech': ['food delivery', 'restaurant', 'food'],
    'ecommerce': ['ecommerce', 'e-commerce', 'online retail', 'marketplace'],
    'logistics': ['logistics', 'delivery', 'transportation'],
    'healthtech': ['health', 'medical', 'pharma', 'healthcare'],
    'agritech': ['agriculture', 'farming', 'agri'],
    'traveltech': ['travel', 'tourism', 'hotel', 'booking'],
}


def get_funding_stats(
    df: pd.DataFrame,
    sector: Optional[str] = None,
    state: Optional[str] = None,
    year: Optional[int] = None,
    round_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive funding statistics with flexible filtering.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned funding dataframe
    sector : str, optional
        Filter by sector (partial string matching, case-insensitive)
    state : str, optional
        Filter by state/city (partial string matching, case-insensitive)
    year : int, optional
        Filter by specific year
    round_type : str, optional
        Filter by funding round type (partial string matching, case-insensitive)
        
    Returns:
    --------
    dict
        Dictionary containing:
        - total_deals: Total number of funding deals
        - total_amount_cr: Total funding amount in Crores
        - avg_amount_cr: Average funding amount in Crores
        - top_investors: Top 5 investors by deal count
        - top_startups: Top 5 startups by total funding
    """
    # Create a copy to avoid modifying original
    filtered_df = df.copy()
    
    # Apply filters with partial string matching (case-insensitive)
    if sector is not None:
        # Check for sector-related columns
        sector_col = find_column(filtered_df, ['sector_standardized', 'sector', 'industry', 'vertical'])
        if sector_col:
            # If sector is a known keyword, use keyword matching (more comprehensive)
            if sector.lower() in SECTOR_KEYWORDS:
                keywords = SECTOR_KEYWORDS[sector.lower()]
                # Create OR condition for all keywords
                pattern = '|'.join(keywords)
                mask = filtered_df[sector_col].str.lower().str.contains(
                    pattern, na=False, regex=True
                )
            else:
                # Otherwise use exact/partial match
                mask = filtered_df[sector_col].str.lower().str.contains(
                    sector.lower(), na=False, regex=False
                )
            
            filtered_df = filtered_df[mask]
    
    if state is not None:
        # Check for state/city/location columns
        state_col = find_column(filtered_df, ['state_standardized', 'state', 'city', 'location'])
        if state_col:
            # If state is in mapping, use city names (more comprehensive)
            if state.lower() in STATE_TO_CITIES:
                cities = STATE_TO_CITIES[state.lower()]
                # Create OR condition for all cities in that state
                pattern = '|'.join(cities)
                mask = filtered_df[state_col].str.lower().str.contains(
                    pattern, na=False, regex=True
                )
            else:
                # Otherwise use exact/partial match
                mask = filtered_df[state_col].str.lower().str.contains(
                    state.lower(), na=False, regex=False
                )
            
            filtered_df = filtered_df[mask]
    
    if year is not None:
        # Check for year column
        year_col = find_column(filtered_df, ['year'])
        if year_col:
            filtered_df = filtered_df[filtered_df[year_col] == year]
    
    if round_type is not None:
        # Check for round type columns
        round_col = find_column(filtered_df, ['round', 'investment_type', 'type'])
        if round_col:
            filtered_df = filtered_df[
                filtered_df[round_col].str.lower().str.contains(
                    round_type.lower(), na=False, regex=False
                )
            ]
    
    # Calculate statistics
    total_deals = len(filtered_df)
    
    # Find amount column
    amount_col = find_column(filtered_df, ['amount_cleaned', 'amount'])
    
    if amount_col and total_deals > 0:
        # Convert to Crores (assuming amount is in rupees)
        # If already in rupees, divide by 10,000,000 to get Crores
        total_amount = filtered_df[amount_col].sum()
        avg_amount = filtered_df[amount_col].mean()
        
        # Convert to Crores (1 Cr = 10,000,000)
        total_amount_cr = total_amount / 10_000_000
        avg_amount_cr = avg_amount / 10_000_000
    else:
        total_amount_cr = 0.0
        avg_amount_cr = 0.0
    
    # Get top investors
    top_investors = get_top_investors(filtered_df)
    
    # Get top startups
    top_startups = get_top_startups(filtered_df)
    
    return {
        'total_deals': total_deals,
        'total_amount_cr': round(total_amount_cr, 2),
        'avg_amount_cr': round(avg_amount_cr, 2),
        'top_investors': top_investors,
        'top_startups': top_startups
    }


def find_column(df: pd.DataFrame, possible_names: list) -> Optional[str]:
    """
    Find column in dataframe by checking multiple possible names.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to search
    possible_names : list
        List of possible column names to check
        
    Returns:
    --------
    str or None
        Column name if found, None otherwise
    """
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for name in possible_names:
        if name.lower() in df_columns_lower:
            return df_columns_lower[name.lower()]
        
        # Check if any column contains the name
        for col_lower, col_original in df_columns_lower.items():
            if name.lower() in col_lower:
                return col_original
    
    return None


def get_top_investors(df: pd.DataFrame, top_n: int = 5) -> Dict[str, int]:
    """
    Get top investors by number of deals.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered funding dataframe
    top_n : int
        Number of top investors to return
        
    Returns:
    --------
    dict
        Dictionary of investor names and deal counts
    """
    investor_col = find_column(df, ['investor', 'investors', 'investor_name'])
    
    if investor_col is None or len(df) == 0:
        return {}
    
    # Count deals per investor
    investor_counts = df[investor_col].value_counts().head(top_n)
    
    return investor_counts.to_dict()


def get_top_startups(df: pd.DataFrame, top_n: int = 5) -> Dict[str, float]:
    """
    Get top startups by total funding amount.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered funding dataframe
    top_n : int
        Number of top startups to return
        
    Returns:
    --------
    dict
        Dictionary of startup names and total funding in Crores
    """
    startup_col = find_column(df, ['startup', 'company', 'startup_name', 'company_name'])
    amount_col = find_column(df, ['amount_cleaned', 'amount'])
    
    if startup_col is None or amount_col is None or len(df) == 0:
        return {}
    
    # Group by startup and sum amounts
    startup_funding = df.groupby(startup_col)[amount_col].sum()
    
    # Convert to Crores and get top N
    startup_funding_cr = (startup_funding / 10_000_000).sort_values(ascending=False).head(top_n)
    
    # Round to 2 decimal places
    return {k: round(v, 2) for k, v in startup_funding_cr.to_dict().items()}


def get_yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get yearly funding trends.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned funding dataframe
        
    Returns:
    --------
    pd.DataFrame
        Yearly statistics including deal count and total funding
    """
    year_col = find_column(df, ['year'])
    amount_col = find_column(df, ['amount_cleaned', 'amount'])
    
    if year_col is None:
        return pd.DataFrame()
    
    # Group by year
    if amount_col:
        yearly_stats = df.groupby(year_col).agg({
            year_col: 'count',
            amount_col: ['sum', 'mean']
        })
        yearly_stats.columns = ['deal_count', 'total_amount', 'avg_amount']
        
        # Convert to Crores
        yearly_stats['total_amount_cr'] = yearly_stats['total_amount'] / 10_000_000
        yearly_stats['avg_amount_cr'] = yearly_stats['avg_amount'] / 10_000_000
    else:
        yearly_stats = df.groupby(year_col).size().to_frame('deal_count')
    
    return yearly_stats


def get_sector_distribution(df: pd.DataFrame, top_n: int = 10) -> Dict[str, int]:
    """
    Get distribution of deals across sectors.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned funding dataframe
    top_n : int
        Number of top sectors to return
        
    Returns:
    --------
    dict
        Dictionary of sector names and deal counts
    """
    sector_col = find_column(df, ['sector', 'industry', 'vertical', 'sector_standardized'])
    
    if sector_col is None:
        return {}
    
    sector_counts = df[sector_col].value_counts().head(top_n)
    
    return sector_counts.to_dict()


def get_state_distribution(df: pd.DataFrame, top_n: int = 10) -> Dict[str, int]:
    """
    Get distribution of deals across states/cities.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned funding dataframe
    top_n : int
        Number of top states to return
        
    Returns:
    --------
    dict
        Dictionary of state/city names and deal counts
    """
    state_col = find_column(df, ['state', 'city', 'location', 'state_standardized'])
    
    if state_col is None:
        return {}
    
    state_counts = df[state_col].value_counts().head(top_n)
    
    return state_counts.to_dict()


def print_stats_summary(stats: Dict[str, Any]) -> None:
    """
    Pretty print funding statistics summary.
    
    Parameters:
    -----------
    stats : dict
        Statistics dictionary from get_funding_stats()
    """
    print("\n" + "="*70)
    print("FUNDING STATISTICS SUMMARY")
    print("="*70)
    
    print(f"\nTotal Deals: {stats['total_deals']:,}")
    print(f"Total Funding: ₹{stats['total_amount_cr']:,.2f} Cr")
    print(f"Average Funding: ₹{stats['avg_amount_cr']:,.2f} Cr")
    
    if stats['top_investors']:
        print("\nTop 5 Investors:")
        for idx, (investor, count) in enumerate(stats['top_investors'].items(), 1):
            print(f"  {idx}. {investor}: {count} deals")
    
    if stats['top_startups']:
        print("\nTop 5 Startups by Funding:")
        for idx, (startup, amount) in enumerate(stats['top_startups'].items(), 1):
            print(f"  {idx}. {startup}: ₹{amount:,.2f} Cr")
    
    print("\n" + "="*70)
