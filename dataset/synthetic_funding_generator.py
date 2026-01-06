"""
Synthetic Indian Startup Funding Dataset Generator (2010-2025)
Creates realistic funding data based on actual Indian startup ecosystem trends
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ==================== DATA CONFIGURATION ====================

# Real Indian Startups by Era (2010-2025)
STARTUPS = {
    '2010-2012': [
        'Flipkart', 'Snapdeal', 'Myntra', 'InMobi', 'MakeMyTrip', 'Naukri',
        'Zomato', 'Freshdesk', 'Redbus', 'BookMyShow', 'Practo', 'UrbanClap',
        'Housing.com', 'CommonFloor', 'PolicyBazaar', 'BankBazaar', 'Freecharge',
        'ClearTrip', 'Yatra', 'GoIbibo', 'Ola', 'TaxiForSure', 'Meru Cabs',
        'Portea Medical', 'Lenskart', 'CarDekho', 'CarTrade', 'Quikr', 'OLX India',
        'JustDial', 'Hike Messenger', 'Shaadi.com', 'BharatMatrimony', 'MoneyTap'
    ],
    '2013-2015': [
        'Swiggy', 'Grofers', 'BigBasket', 'UrbanLadder', 'Pepperfry', 'FabFurnish',
        'PayTM', 'PhonePe', 'MobiKwik', 'Razorpay', 'Zerodha', 'Upstox', 'Groww',
        'CRED', 'Dunzo', 'Meesho', 'Shopclues', 'FirstCry', 'Lybrate', 'HealthifyMe',
        'Cure.fit', 'Ather Energy', 'Rivigo', 'BlackBuck', 'Delhivery', 'Ecom Express',
        'Udaan', 'NinjaCart', 'WayCool', 'DeHaat', 'AgroStar', 'Ninjacart',
        'BYJU\'S', 'Unacademy', 'Vedantu', 'Toppr', 'upGrad', 'Simplilearn'
    ],
    '2016-2018': [
        'Oyo', 'OYO Rooms', 'FabHotels', 'Zostel', 'Treebo', 'Bounce', 'Vogo',
        'Yulu', 'Rapido', 'Zoomcar', 'Drivezy', 'Revv', 'Cars24', 'Spinny',
        'Dream11', 'MPL', 'Mobile Premier League', 'Paytm First Games', 'Haptik',
        'Yellow Messenger', 'Verloop.io', 'Acko', 'Digit Insurance', 'Go Digit',
        'Cars24', 'CarDekho', 'Droom', 'CarWale', 'Zetwerk', 'Infra.Market',
        'OfBusiness', 'Moglix', 'Udaan', 'Shiprocket', 'Xpressbees', 'Shadowfax'
    ],
    '2019-2021': [
        'ShareChat', 'Josh', 'Moj', 'Chingari', 'Roposo', 'Ula', 'Glance',
        'DailyHunt', 'InShorts', 'The Ken', 'Apna', 'BharatPe', 'Khatabook',
        'OkCredit', 'M2P Fintech', 'Slice', 'Jupiter', 'FamPay', 'Niyo',
        'Jar', 'Jumbotail', 'ElasticRun', 'DealShare', 'CityMall', 'SimplyNadu',
        'Licious', 'FreshToHome', 'Zappfresh', 'Country Delight', 'Milkbasket',
        'Blinkit', 'Zepto', 'Dunzo Daily', 'Flipkart Quick', 'Amazon Fresh'
    ],
    '2022-2025': [
        'ONDC', 'Open Network', 'Ola Electric', 'Ather Energy', 'Simple Energy',
        'Ultraviolette', 'Revolt Motors', 'Blue Smart', 'BluSmart', 'Blu Smart Mobility',
        'CredAvenue', 'CredFlow', 'KreditBee', 'EarlySalary', 'MoneyView',
        'Stable Money', 'INDmoney', 'Scripbox', 'ET Money', 'Ditto Insurance',
        'Plum Insurance', 'The HealthInsurance', 'Arya.ag', 'CropIn', 'Ninjacart',
        'Captain Fresh', 'FreshToHome', 'Waycool Foods', 'Vegrow', 'DeHaat',
        'KissanKraft', 'Tractor Junction', 'Atomberg', 'boAt', 'Noise',
        'Fire-Boltt', 'Zebronics', 'Mamaearth', 'Wow Skin Science', 'mCaffeine',
        'Pilgrim', 'Sugar Cosmetics', 'MyGlamm', 'Purplle', 'Nykaa Fashion'
    ]
}

# Sector standardization with era-specific trends
SECTORS = {
    'E-Commerce': ['2010-2025', 0.18],
    'Fintech': ['2013-2025', 0.16],
    'Edtech': ['2015-2025', 0.12],
    'Healthtech': ['2014-2025', 0.10],
    'Logistics': ['2014-2025', 0.09],
    'Foodtech': ['2013-2025', 0.08],
    'Mobility': ['2013-2025', 0.07],
    'SaaS': ['2012-2025', 0.06],
    'Agritech': ['2016-2025', 0.05],
    'Gaming': ['2017-2025', 0.04],
    'Social Media': ['2015-2025', 0.03],
    'Deeptech': ['2018-2025', 0.02]
}

# Major Indian cities with tier classification
CITIES = {
    'Tier 1': ['Bangalore', 'Mumbai', 'Gurgaon', 'Delhi', 'Hyderabad', 'Pune', 'Chennai'],
    'Tier 2': ['Ahmedabad', 'Kolkata', 'Jaipur', 'Chandigarh', 'Indore', 'Kochi', 'Coimbatore', 'Lucknow'],
    'Tier 3': ['Surat', 'Vadodara', 'Nagpur', 'Bhubaneswar', 'Visakhapatnam', 'Thiruvananthapuram', 'Mysore']
}

# State mapping
STATE_MAP = {
    'Bangalore': 'Karnataka', 'Mumbai': 'Maharashtra', 'Gurgaon': 'Haryana', 
    'Delhi': 'Delhi', 'Hyderabad': 'Telangana', 'Pune': 'Maharashtra',
    'Chennai': 'Tamil Nadu', 'Ahmedabad': 'Gujarat', 'Kolkata': 'West Bengal',
    'Jaipur': 'Rajasthan', 'Chandigarh': 'Chandigarh', 'Indore': 'Madhya Pradesh',
    'Kochi': 'Kerala', 'Coimbatore': 'Tamil Nadu', 'Lucknow': 'Uttar Pradesh',
    'Surat': 'Gujarat', 'Vadodara': 'Gujarat', 'Nagpur': 'Maharashtra',
    'Bhubaneswar': 'Odisha', 'Visakhapatnam': 'Andhra Pradesh', 
    'Thiruvananthapuram': 'Kerala', 'Mysore': 'Karnataka'
}

# Investor categories with era trends
INVESTORS = {
    'Domestic VC': [
        'Sequoia Capital India', 'Accel India', 'Blume Ventures', 'Kalaari Capital',
        'Nexus Venture Partners', 'Chiratae Ventures', 'Matrix Partners India',
        'Saama Capital', 'Lightspeed India', 'SAIF Partners', 'Fireside Ventures',
        'Elevation Capital', 'Peak XV Partners'
    ],
    'Foreign VC': [
        'Tiger Global', 'SoftBank Vision Fund', 'Sequoia Capital', 'Accel Partners',
        'Lightspeed Venture Partners', 'Andreessen Horowitz', 'General Atlantic',
        'Naspers', 'Tencent', 'Alibaba', 'Steadview Capital', 'Coatue Management'
    ],
    'Corporate VC': [
        'Google Ventures', 'Amazon Ventures', 'Flipkart Ventures', 'Times Internet',
        'Infosys Innovation Fund', 'TCS Ventures', 'Reliance Ventures', 
        'Aditya Birla Ventures', 'Wipro Ventures', 'Qualcomm Ventures'
    ],
    'Angel/HNI': [
        'Ratan Tata', 'Kunal Shah', 'Sachin Bansal', 'Binny Bansal', 
        'Vijay Shekhar Sharma', 'Bhavish Aggarwal', 'Deepinder Goyal',
        'Ritesh Agarwal', 'Falguni Nayar', 'Indian Angel Network', 'Mumbai Angels'
    ],
    'PE Funds': [
        'Warburg Pincus', 'KKR India', 'TPG Capital', 'Carlyle Group',
        'Blackstone', 'ChrysCapital', 'Multiples Alternate Asset Management',
        'Everstone Capital', 'ICICI Venture', 'Kedaara Capital'
    ]
}

# Funding stage multipliers (in USD Million)
FUNDING_STAGES = {
    'Seed': (0.1, 2),
    'Pre-Series A': (0.5, 5),
    'Series A': (3, 15),
    'Series B': (10, 50),
    'Series C': (30, 150),
    'Series D': (60, 300),
    'Series E+': (100, 1000),
    'Bridge': (2, 20),
    'Debt': (5, 100),
    'Growth': (50, 500)
}

# Year-wise funding intensity (multiplier for number of deals)
YEAR_INTENSITY = {
    2010: 0.3, 2011: 0.4, 2012: 0.5, 2013: 0.7, 2014: 1.0,
    2015: 1.3, 2016: 1.5, 2017: 1.8, 2018: 2.0, 2019: 2.2,
    2020: 1.7, 2021: 3.0, 2022: 2.5, 2023: 1.8, 2024: 2.0, 2025: 2.1
}

# Currency conversion rates (historical average INR to USD)
USD_TO_INR = {
    2010: 45.73, 2011: 46.67, 2012: 53.44, 2013: 58.60, 2014: 61.03,
    2015: 64.15, 2016: 67.20, 2017: 65.12, 2018: 68.39, 2019: 70.42,
    2020: 74.10, 2021: 73.50, 2022: 78.60, 2023: 82.60, 2024: 83.25, 2025: 84.50
}


def generate_random_date(year):
    """Generate random date within a year"""
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def select_city_by_year(year):
    """Select city based on startup ecosystem maturity"""
    if year <= 2014:
        # Early years: 90% Tier 1 cities
        tier_prob = [0.90, 0.08, 0.02]
    elif year <= 2018:
        # Growth phase: 70% Tier 1, 25% Tier 2
        tier_prob = [0.70, 0.25, 0.05]
    else:
        # Mature phase: More distribution
        tier_prob = [0.60, 0.30, 0.10]
    
    tier = np.random.choice(['Tier 1', 'Tier 2', 'Tier 3'], p=tier_prob)
    city = random.choice(CITIES[tier])
    return city, STATE_MAP[city]


def select_sector_by_year(year):
    """Select sector based on era trends"""
    available_sectors = []
    weights = []
    
    for sector, (era_range, weight) in SECTORS.items():
        start_year, end_year = map(int, era_range.split('-'))
        if start_year <= year <= end_year:
            available_sectors.append(sector)
            weights.append(weight)
    
    # Normalize weights
    total = sum(weights)
    weights = [w/total for w in weights]
    
    return np.random.choice(available_sectors, p=weights)


def select_investors(year, funding_amount_usd):
    """Select investors based on deal size and era"""
    num_investors = 1
    
    # Larger deals have more investors
    if funding_amount_usd > 100:
        num_investors = random.randint(2, 5)
    elif funding_amount_usd > 50:
        num_investors = random.randint(1, 3)
    elif funding_amount_usd > 10:
        num_investors = random.randint(1, 2)
    
    # Select investor categories based on year and amount
    investor_list = []
    
    for _ in range(num_investors):
        if funding_amount_usd > 100:
            # Large deals: More foreign VCs and PE
            categories = ['Foreign VC', 'PE Funds', 'Domestic VC']
            weights = [0.5, 0.3, 0.2]
        elif funding_amount_usd > 20:
            # Medium deals: Mix of VCs
            categories = ['Domestic VC', 'Foreign VC', 'Corporate VC']
            weights = [0.5, 0.35, 0.15]
        else:
            # Small deals: Angels and domestic VCs
            categories = ['Domestic VC', 'Angel/HNI']
            weights = [0.6, 0.4]
        
        category = np.random.choice(categories, p=weights)
        investor = random.choice(INVESTORS[category])
        
        if investor not in investor_list:
            investor_list.append(investor)
    
    return ', '.join(investor_list)


def select_funding_stage(year, company_name, previous_stages):
    """Select funding stage based on company maturity"""
    # Determine company age (approximate)
    company_start_year = year
    
    # Check which era the company belongs to
    for era, companies in STARTUPS.items():
        if company_name in companies:
            era_start = int(era.split('-')[0])
            company_start_year = max(era_start, year - random.randint(0, 3))
            break
    
    company_age = year - company_start_year
    
    # Stage progression
    if company_age == 0:
        stages = ['Seed', 'Pre-Series A']
        weights = [0.7, 0.3]
    elif company_age == 1:
        stages = ['Pre-Series A', 'Series A', 'Bridge']
        weights = [0.3, 0.6, 0.1]
    elif company_age == 2:
        stages = ['Series A', 'Series B', 'Bridge']
        weights = [0.3, 0.6, 0.1]
    elif company_age == 3:
        stages = ['Series B', 'Series C', 'Debt']
        weights = [0.3, 0.5, 0.2]
    elif company_age >= 4:
        stages = ['Series C', 'Series D', 'Series E+', 'Growth', 'Debt']
        weights = [0.25, 0.25, 0.2, 0.2, 0.1]
    else:
        stages = ['Seed']
        weights = [1.0]
    
    return np.random.choice(stages, p=weights)


def generate_funding_amount(year, stage, sector):
    """Generate realistic funding amount"""
    min_amount, max_amount = FUNDING_STAGES[stage]
    
    # Sector multipliers
    sector_multipliers = {
        'E-Commerce': 1.5,
        'Fintech': 1.3,
        'Mobility': 1.4,
        'Logistics': 1.2,
        'Edtech': 1.0,
        'Healthtech': 0.9,
        'Foodtech': 1.1,
        'SaaS': 0.8,
        'Agritech': 0.7,
        'Gaming': 0.9,
        'Social Media': 1.2,
        'Deeptech': 0.8
    }
    
    multiplier = sector_multipliers.get(sector, 1.0)
    
    # Year-based adjustment (funding bubble 2021, correction 2022-23)
    if year >= 2020 and year <= 2021:
        year_mult = 1.5
    elif year >= 2022 and year <= 2023:
        year_mult = 0.7
    else:
        year_mult = 1.0
    
    # Generate amount with log-normal distribution
    mean = (min_amount + max_amount) / 2
    std = (max_amount - min_amount) / 4
    
    amount_usd = np.random.lognormal(np.log(mean), 0.5) * multiplier * year_mult
    amount_usd = np.clip(amount_usd, min_amount, max_amount * 2)  # Allow some outliers
    
    # Convert to INR - USD values are in millions, so multiply by 1,000,000 first
    amount_inr = amount_usd * 1_000_000 * USD_TO_INR[year]
    
    return amount_usd, amount_inr


def format_amount(amount_inr):
    """Format amount in Indian currency style"""
    if amount_inr >= 10000000:  # 1 Cr+
        crores = amount_inr / 10000000
        return f"₹{crores:.2f} Cr"
    elif amount_inr >= 100000:  # 1 L+
        lakhs = amount_inr / 100000
        return f"₹{lakhs:.2f} L"
    else:
        # For very small amounts, still show in Lakhs
        lakhs = amount_inr / 100000
        return f"₹{lakhs:.3f} L"


def generate_dataset(target_records=15000):
    """Generate comprehensive synthetic dataset"""
    
    print("🚀 Starting Synthetic Funding Data Generation...")
    print(f"📊 Target: {target_records} funding records (2010-2025)")
    print("=" * 70)
    
    records = []
    company_funding_history = {}  # Track funding stages per company
    company_sector_mapping = {}  # Track consistent sector per company
    
    for year in range(2010, 2026):
        year_intensity = YEAR_INTENSITY[year]
        num_records_year = int((target_records / 16) * year_intensity)  # 16 years
        
        print(f"\n📅 Generating {num_records_year} records for {year}...")
        
        # Select companies for this year
        available_companies = []
        for era, companies in STARTUPS.items():
            era_start, era_end = map(int, era.split('-'))
            if era_start <= year <= era_end + 3:  # Companies can raise funds 3 years after era
                available_companies.extend(companies)
        
        for i in range(num_records_year):
            company_name = random.choice(available_companies)
            
            # Get previous stages for this company
            previous_stages = company_funding_history.get(company_name, [])
            
            # Generate funding details
            date = generate_random_date(year)
            
            # Use consistent sector for each company
            if company_name not in company_sector_mapping:
                company_sector_mapping[company_name] = select_sector_by_year(year)
            sector = company_sector_mapping[company_name]
            
            city, state = select_city_by_year(year)
            stage = select_funding_stage(year, company_name, previous_stages)
            amount_usd, amount_inr = generate_funding_amount(year, stage, sector)
            investors = select_investors(year, amount_usd)
            amount_formatted = format_amount(amount_inr)
            
            # Update company history
            if company_name not in company_funding_history:
                company_funding_history[company_name] = []
            company_funding_history[company_name].append(stage)
            
            record = {
                'Startup Name': company_name,
                'Amount_Cleaned': amount_formatted,
                'Amount_USD': f"${amount_usd:.2f}M",
                'Amount_INR_Numeric': amount_inr,
                'Sector_Standardized': sector,
                'City': city,
                'State_Standardized': state,
                'Investors\' Name': investors,
                'Funding_Stage': stage,
                'Date_Parsed': date.strftime('%Y-%m-%d'),
                'Year': year,
                'Quarter': f"Q{(date.month-1)//3 + 1}",
                'Month': date.strftime('%B')
            }
            
            records.append(record)
        
        print(f"   ✅ Generated {num_records_year} records | Total: {len(records)}")
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Shuffle to mix years
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n" + "=" * 70)
    print(f"✨ Dataset Generation Complete!")
    print(f"📈 Total Records: {len(df)}")
    print(f"📅 Date Range: {df['Year'].min()} - {df['Year'].max()}")
    print(f"🏢 Unique Companies: {df['Startup Name'].nunique()}")
    print(f"🏭 Sectors: {df['Sector_Standardized'].nunique()}")
    print(f"🌆 Cities: {df['City'].nunique()}")
    print(f"💰 Total Funding: ₹{df['Amount_INR_Numeric'].sum() / 10000000:.2f} Cr")
    print("=" * 70)
    
    return df


def generate_statistics(df):
    """Generate dataset statistics"""
    
    print("\n📊 DATASET STATISTICS")
    print("=" * 70)
    
    # Year-wise breakdown
    print("\n📅 Year-wise Funding:")
    year_stats = df.groupby('Year').agg({
        'Startup Name': 'count',
        'Amount_INR_Numeric': 'sum'
    }).rename(columns={'Startup Name': 'Deals', 'Amount_INR_Numeric': 'Amount_INR'})
    year_stats['Amount_Cr'] = year_stats['Amount_INR'] / 10000000
    print(year_stats[['Deals', 'Amount_Cr']].to_string())
    
    # Sector-wise breakdown
    print("\n🏭 Top 10 Sectors by Deal Count:")
    sector_stats = df['Sector_Standardized'].value_counts().head(10)
    print(sector_stats.to_string())
    
    # City-wise breakdown
    print("\n🌆 Top 10 Cities:")
    city_stats = df['City'].value_counts().head(10)
    print(city_stats.to_string())
    
    # Top funded companies
    print("\n💰 Top 15 Most Funded Companies:")
    company_funding = df.groupby('Startup Name')['Amount_INR_Numeric'].sum().sort_values(ascending=False).head(15)
    company_funding_cr = company_funding / 10000000
    print(company_funding_cr.to_string())
    
    print("\n" + "=" * 70)


def save_dataset(df, filename='cleaned_funding_synthetic_2010_2025.csv'):
    """Save dataset to CSV"""
    # Prepare final columns to match original format
    final_df = df[[
        'Startup Name', 'Amount_Cleaned', 'Sector_Standardized',
        'City', 'State_Standardized', 'Investors\' Name',
        'Date_Parsed', 'Year'
    ]].copy()
    
    final_df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n💾 Dataset saved to: {filename}")
    print(f"📦 File size: {len(df)} records")
    
    # Also save with extended columns
    extended_filename = filename.replace('.csv', '_extended.csv')
    df.to_csv(extended_filename, index=False, encoding='utf-8-sig')
    print(f"💾 Extended dataset saved to: {extended_filename}")
    
    # Save metadata
    metadata = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_records': len(df),
        'date_range': f"{df['Year'].min()}-{df['Year'].max()}",
        'unique_companies': int(df['Startup Name'].nunique()),
        'unique_sectors': int(df['Sector_Standardized'].nunique()),
        'unique_cities': int(df['City'].nunique()),
        'total_funding_inr_cr': float(df['Amount_INR_Numeric'].sum() / 10000000),
        'columns': list(df.columns)
    }
    
    with open(filename.replace('.csv', '_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"📋 Metadata saved to: {filename.replace('.csv', '_metadata.json')}")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    # Generate dataset
    df = generate_dataset(target_records=15000)
    
    # Show statistics
    generate_statistics(df)
    
    # Save to files
    save_dataset(df)
    
    print("\n🎉 All Done! Your synthetic dataset is ready for the RAG system!")
    print("=" * 70)
