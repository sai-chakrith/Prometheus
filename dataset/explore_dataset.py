"""
Dataset Explorer - Interactive analysis of the synthetic funding dataset
"""

import pandas as pd
import json

def load_dataset():
    """Load the main dataset"""
    return pd.read_csv('cleaned_funding_synthetic_2010_2025.csv')

def load_extended_dataset():
    """Load the extended dataset"""
    return pd.read_csv('cleaned_funding_synthetic_2010_2025_extended.csv')

def load_metadata():
    """Load metadata"""
    with open('cleaned_funding_synthetic_2010_2025_metadata.json', 'r') as f:
        return json.load(f)

def explore_menu():
    """Interactive exploration menu"""
    
    print("\n" + "=" * 70)
    print("📊 SYNTHETIC FUNDING DATASET EXPLORER")
    print("=" * 70)
    
    df = load_dataset()
    df_ext = load_extended_dataset()
    metadata = load_metadata()
    
    while True:
        print("\n🔍 Choose an analysis:")
        print("1. Year-wise funding trends")
        print("2. Sector analysis")
        print("3. City/State distribution")
        print("4. Company deep dive")
        print("5. Investor analysis")
        print("6. Search by company name")
        print("7. Search by sector")
        print("8. Search by city")
        print("9. Dataset statistics")
        print("10. Sample queries for RAG testing")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-10): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            year_wise_analysis(df_ext)
        elif choice == '2':
            sector_analysis(df)
        elif choice == '3':
            location_analysis(df)
        elif choice == '4':
            company_deep_dive(df_ext)
        elif choice == '5':
            investor_analysis(df)
        elif choice == '6':
            search_by_company(df_ext)
        elif choice == '7':
            search_by_sector(df)
        elif choice == '8':
            search_by_city(df)
        elif choice == '9':
            show_statistics(metadata)
        elif choice == '10':
            sample_queries()
        else:
            print("❌ Invalid choice. Please try again.")

def year_wise_analysis(df):
    """Analyze funding trends by year"""
    print("\n📅 YEAR-WISE FUNDING TRENDS")
    print("=" * 70)
    
    yearly = df.groupby('Year').agg({
        'Startup Name': 'count',
        'Amount_INR_Numeric': 'sum'
    })
    yearly.columns = ['Total Deals', 'Total Amount (INR)']
    yearly['Avg Deal Size (Cr)'] = (yearly['Total Amount (INR)'] / yearly['Total Deals']) / 10000000
    yearly['Total Amount (Cr)'] = yearly['Total Amount (INR)'] / 10000000
    
    print(yearly[['Total Deals', 'Total Amount (Cr)', 'Avg Deal Size (Cr)']].to_string())
    
    print("\n📈 Growth Insights:")
    print(f"- Peak year (deals): {yearly['Total Deals'].idxmax()} with {yearly['Total Deals'].max()} deals")
    print(f"- Peak year (amount): {yearly['Total Amount (Cr)'].idxmax()} with ₹{yearly['Total Amount (Cr)'].max():.2f} Cr")
    print(f"- Largest avg deal: {yearly['Avg Deal Size (Cr)'].idxmax()} with ₹{yearly['Avg Deal Size (Cr)'].max():.2f} Cr")

def sector_analysis(df):
    """Analyze by sector"""
    print("\n🏭 SECTOR ANALYSIS")
    print("=" * 70)
    
    print("\n📊 Top Sectors by Deal Count:")
    sector_counts = df['Sector_Standardized'].value_counts()
    for sector, count in sector_counts.items():
        pct = (count / len(df)) * 100
        print(f"{sector:20s}: {count:5d} deals ({pct:.1f}%)")
    
    print("\n💰 Want to see funding amounts by sector? (y/n): ", end='')
    if input().strip().lower() == 'y':
        df_ext = load_extended_dataset()
        sector_funding = df_ext.groupby('Sector_Standardized')['Amount_INR_Numeric'].sum() / 10000000
        sector_funding = sector_funding.sort_values(ascending=False)
        print("\n💸 Total Funding by Sector (Crores):")
        print(sector_funding.to_string())

def location_analysis(df):
    """Analyze by location"""
    print("\n🌆 LOCATION ANALYSIS")
    print("=" * 70)
    
    print("\n🏙️ Top 15 Cities by Deal Count:")
    city_counts = df['City'].value_counts().head(15)
    print(city_counts.to_string())
    
    print("\n🗺️ State-wise Distribution:")
    state_counts = df['State_Standardized'].value_counts()
    print(state_counts.to_string())

def company_deep_dive(df):
    """Deep dive into company funding history"""
    print("\n🏢 COMPANY DEEP DIVE")
    print("=" * 70)
    
    print("\n📈 Top 20 Most Active Companies:")
    company_counts = df['Startup Name'].value_counts().head(20)
    print(company_counts.to_string())
    
    print("\n🔍 Enter company name to see detailed history (or press Enter to skip): ", end='')
    company = input().strip()
    
    if company:
        company_data = df[df['Startup Name'].str.contains(company, case=False, na=False)]
        
        if len(company_data) == 0:
            print(f"❌ No data found for '{company}'")
        else:
            print(f"\n📊 Funding History for '{company_data.iloc[0]['Startup Name']}':")
            print("=" * 70)
            
            for _, row in company_data.sort_values('Date_Parsed').iterrows():
                print(f"\n📅 {row['Date_Parsed']} ({row['Year']})")
                print(f"   Stage: {row.get('Funding_Stage', 'N/A')}")
                print(f"   Amount: {row['Amount_Cleaned']}")
                print(f"   Sector: {row['Sector_Standardized']}")
                print(f"   City: {row['City']}, {row['State_Standardized']}")
                print(f"   Investors: {row['Investors\\' Name']}")
            
            print(f"\n📊 Summary:")
            print(f"   Total Rounds: {len(company_data)}")
            print(f"   Total Funding: ₹{company_data['Amount_INR_Numeric'].sum() / 10000000:.2f} Cr")
            print(f"   Avg Round Size: ₹{company_data['Amount_INR_Numeric'].mean() / 10000000:.2f} Cr")

def investor_analysis(df):
    """Analyze investor participation"""
    print("\n💼 INVESTOR ANALYSIS")
    print("=" * 70)
    
    # Split investors and count
    all_investors = df['Investors\\' Name'].str.split(', ').explode()
    investor_counts = all_investors.value_counts().head(20)
    
    print("\n🏆 Top 20 Most Active Investors:")
    print(investor_counts.to_string())

def search_by_company(df):
    """Search funding by company name"""
    print("\n🔍 SEARCH BY COMPANY")
    print("=" * 70)
    
    search_term = input("\nEnter company name (partial match): ").strip()
    
    if not search_term:
        print("❌ Please enter a search term")
        return
    
    results = df[df['Startup Name'].str.contains(search_term, case=False, na=False)]
    
    if len(results) == 0:
        print(f"\n❌ No results found for '{search_term}'")
    else:
        print(f"\n✅ Found {len(results)} funding rounds:")
        print(results[['Date_Parsed', 'Startup Name', 'Amount_Cleaned', 'Sector_Standardized', 'City']].to_string())

def search_by_sector(df):
    """Search by sector"""
    print("\n🔍 SEARCH BY SECTOR")
    print("=" * 70)
    
    print("\nAvailable sectors:")
    sectors = df['Sector_Standardized'].unique()
    for i, sector in enumerate(sectors, 1):
        print(f"{i}. {sector}")
    
    sector = input("\nEnter sector name: ").strip()
    
    if not sector:
        return
    
    results = df[df['Sector_Standardized'].str.contains(sector, case=False, na=False)]
    
    print(f"\n✅ Found {len(results)} deals in {sector}")
    print(f"📊 Summary:")
    print(f"   Companies: {results['Startup Name'].nunique()}")
    print(f"   Date Range: {results['Year'].min()} - {results['Year'].max()}")
    print(f"   Top Cities: {results['City'].value_counts().head(5).to_dict()}")

def search_by_city(df):
    """Search by city"""
    print("\n🔍 SEARCH BY CITY")
    print("=" * 70)
    
    city = input("\nEnter city name: ").strip()
    
    if not city:
        return
    
    results = df[df['City'].str.contains(city, case=False, na=False)]
    
    if len(results) == 0:
        print(f"\n❌ No results found for '{city}'")
    else:
        print(f"\n✅ Found {len(results)} deals in {city}")
        print(f"\n📊 Sector Distribution:")
        print(results['Sector_Standardized'].value_counts().to_string())
        
        print(f"\n🏢 Top Companies:")
        print(results['Startup Name'].value_counts().head(10).to_string())

def show_statistics(metadata):
    """Show dataset metadata"""
    print("\n📊 DATASET METADATA")
    print("=" * 70)
    
    for key, value in metadata.items():
        print(f"{key:25s}: {value}")

def sample_queries():
    """Show sample queries for RAG testing"""
    print("\n🤖 SAMPLE QUERIES FOR RAG SYSTEM TESTING")
    print("=" * 70)
    
    queries = {
        "Company Queries": [
            "Tell me about Flipkart funding",
            "Swiggy के बारे में बताओ",
            "BYJU'S ची माहिती दे",
            "What is Zomato's funding history?"
        ],
        "Location Queries": [
            "Show me startups from Bangalore",
            "Mumbai में कौन सी कंपनियाँ हैं?",
            "Which companies are in Hyderabad?",
            "Pune startups list"
        ],
        "Sector Queries": [
            "Fintech startups in India",
            "E-commerce funding trends",
            "Edtech companies",
            "Healthcare startups"
        ],
        "Year Queries": [
            "Funding in 2021",
            "2015 to 2020 investments",
            "Recent funding rounds",
            "2024 startups"
        ],
        "Investor Queries": [
            "Sequoia Capital investments",
            "Tiger Global portfolio",
            "Who invested in Ola?",
            "Accel India funded companies"
        ],
        "Complex Queries": [
            "Fintech startups from Bangalore funded in 2021",
            "E-commerce companies that raised more than 100 crores",
            "Compare Swiggy and Zomato funding",
            "Unicorns in Edtech sector"
        ],
        "Multilingual Queries": [
            "बैंगलोर में fintech स्टार्टअप कौन से हैं?",
            "मुंबईतील स्टार्टअप कोणते आहेत?",
            "Zomato எவ்வளவு funding பெற்றது?",
            "BYJU'S సంస్థ గురించి చెప్పండి"
        ]
    }
    
    for category, query_list in queries.items():
        print(f"\n📝 {category}:")
        for i, query in enumerate(query_list, 1):
            print(f"   {i}. {query}")
    
    print("\n💡 These queries test:")
    print("   ✓ Company-specific information retrieval")
    print("   ✓ Geographic filtering")
    print("   ✓ Sector analysis")
    print("   ✓ Temporal queries")
    print("   ✓ Investor matching")
    print("   ✓ Multi-field complex queries")
    print("   ✓ Multilingual support (8 languages)")

if __name__ == "__main__":
    try:
        explore_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
