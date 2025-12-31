import pandas as pd
import numpy as np
import os
import re
from pathlib import Path


def clean_amount(amount_str):
    """
    Clean and convert amount string to numeric value.
    Handles ₹, $, Cr (Crores) conversion.
    1 Cr = 10 Million = 10,000,000
    """
    if pd.isna(amount_str) or amount_str == '' or amount_str == 'Undisclosed':
        return np.nan
    
    # Convert to string and strip whitespace
    amount_str = str(amount_str).strip()
    
    # Remove currency symbols (₹, $)
    amount_str = amount_str.replace('₹', '').replace('$', '').replace(',', '').strip()
    
    # Handle Crores (Cr) - multiply by 10,000,000
    if 'Cr' in amount_str or 'cr' in amount_str:
        # Extract numeric part
        numeric_part = re.findall(r'[\d.]+', amount_str)
        if numeric_part:
            return float(numeric_part[0]) * 10_000_000
    
    # Handle Millions (M)
    elif 'M' in amount_str or 'm' in amount_str:
        numeric_part = re.findall(r'[\d.]+', amount_str)
        if numeric_part:
            return float(numeric_part[0]) * 1_000_000
    
    # Handle Thousands (K)
    elif 'K' in amount_str or 'k' in amount_str:
        numeric_part = re.findall(r'[\d.]+', amount_str)
        if numeric_part:
            return float(numeric_part[0]) * 1_000
    
    # Try direct numeric conversion
    else:
        try:
            return float(amount_str)
        except ValueError:
            return np.nan


def load_and_clean_data(data_path='data/startups_funding.csv'):
    """
    Load and clean the Startups Funding Dataset.
    
    Parameters:
    -----------
    data_path : str
        Path to the CSV file or directory with monthly CSV files
        
    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe
    """
    print(f"Loading data from {data_path}...")
    
    # Check if the single file exists
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        # Try loading from monthly CSV files in StartUp_FundingScrappingData
        scraping_data_dir = 'StartUp_FundingScrappingData'
        if os.path.exists(scraping_data_dir):
            print(f"Single file not found. Loading from {scraping_data_dir}...")
            
            all_dfs = []
            years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021']
            
            for year in years:
                year_dir = os.path.join(scraping_data_dir, year)
                if os.path.exists(year_dir):
                    print(f"  Loading {year} data...")
                    for csv_file in os.listdir(year_dir):
                        if csv_file.endswith('.csv'):
                            file_path = os.path.join(year_dir, csv_file)
                            try:
                                temp_df = pd.read_csv(file_path)
                                all_dfs.append(temp_df)
                            except Exception as e:
                                print(f"    Warning: Could not load {csv_file}: {str(e)}")
            
            if all_dfs:
                df = pd.concat(all_dfs, ignore_index=True)
                print(f"  Merged {len(all_dfs)} CSV files")
            else:
                raise FileNotFoundError(f"No CSV files found in {scraping_data_dir}")
        else:
            raise FileNotFoundError(f"Data not found at {data_path} or {scraping_data_dir}")
    
    print(f"Loaded {len(df)} records")
    print(f"Columns: {df.columns.tolist()}")
    
    # Clean Amount column
    print("\nCleaning Amount column...")
    amount_col = None
    for col in df.columns:
        if 'amount' in col.lower():
            amount_col = col
            break
    
    if amount_col:
        df['Amount_Cleaned'] = df[amount_col].apply(clean_amount)
        print(f"Cleaned {df['Amount_Cleaned'].notna().sum()} amount values")
    
    # Parse Date column and extract Year
    print("\nParsing Date column...")
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break
    
    if date_col:
        df['Date_Parsed'] = pd.to_datetime(df[date_col], errors='coerce', format='mixed')
        df['Year'] = df['Date_Parsed'].dt.year
        print(f"Extracted year for {df['Year'].notna().sum()} records")
    
    # Standardize Sector to lowercase
    print("\nStandardizing Sector...")
    sector_col = None
    for col in df.columns:
        if 'sector' in col.lower() or 'industry' in col.lower():
            sector_col = col
            break
    
    if sector_col:
        df['Sector_Standardized'] = df[sector_col].str.lower().str.strip()
        print(f"Standardized {df['Sector_Standardized'].notna().sum()} sector values")
    
    # Standardize State/City to lowercase
    print("\nStandardizing State/City...")
    state_col = None
    for col in df.columns:
        if 'state' in col.lower() or 'city' in col.lower() or 'location' in col.lower():
            state_col = col
            break
    
    if state_col:
        df['State_Standardized'] = df[state_col].str.lower().str.strip()
        print(f"Standardized {df['State_Standardized'].notna().sum()} state/city values")
    
    return df


def save_cleaned_data(df, output_path='data/cleaned_funding.csv'):
    """
    Save cleaned dataframe to CSV.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned dataframe
    output_path : str
        Path to save the cleaned CSV
    """
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving cleaned data to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"Saved successfully!")


def print_summary_stats(df):
    """
    Print summary statistics of the cleaned dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned dataframe
    """
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    print(f"\nTotal Records: {len(df)}")
    
    # Amount statistics
    if 'Amount_Cleaned' in df.columns:
        print(f"\nAmount Statistics:")
        print(f"  Valid amounts: {df['Amount_Cleaned'].notna().sum()}")
        print(f"  Missing amounts: {df['Amount_Cleaned'].isna().sum()}")
        if df['Amount_Cleaned'].notna().sum() > 0:
            print(f"  Mean amount: ₹{df['Amount_Cleaned'].mean():,.2f}")
            print(f"  Median amount: ₹{df['Amount_Cleaned'].median():,.2f}")
            print(f"  Total funding: ₹{df['Amount_Cleaned'].sum():,.2f}")
    
    # Year statistics
    if 'Year' in df.columns:
        print(f"\nYear Range:")
        print(f"  Earliest: {df['Year'].min()}")
        print(f"  Latest: {df['Year'].max()}")
        print(f"\nTop 5 Years by Funding Count:")
        print(df['Year'].value_counts().head())
    
    # Sector statistics
    if 'Sector_Standardized' in df.columns:
        print(f"\nTop 5 Sectors by Count:")
        print(df['Sector_Standardized'].value_counts().head())
    
    # State statistics
    if 'State_Standardized' in df.columns:
        print(f"\nTop 5 States/Cities by Count:")
        print(df['State_Standardized'].value_counts().head())
    
    print("\n" + "="*70)


def main():
    """
    Main function to orchestrate data loading and cleaning.
    """
    # Define paths
    data_path = 'data/startups_funding.csv'
    output_path = 'data/cleaned_funding.csv'
    
    # Load and clean data
    df = load_and_clean_data(data_path)
    
    # Save cleaned data
    save_cleaned_data(df, output_path)
    
    # Print summary statistics
    print_summary_stats(df)
    
    # Display first few rows
    print("\nFirst 5 rows of cleaned data:")
    print(df.head())
    
    return df


if __name__ == "__main__":
    df = main()
