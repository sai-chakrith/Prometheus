# Synthetic Indian Startup Funding Dataset (2010-2025)

## 📊 Dataset Overview

This is a **comprehensive synthetic dataset** of Indian startup funding data spanning **15 years (2010-2025)** with **23,243 funding records** across 181 companies. The dataset is designed to be realistic, reflecting actual trends in the Indian startup ecosystem.

## 📁 Files Generated

1. **cleaned_funding_synthetic_2010_2025.csv** (2.0 MB)
   - Standard format compatible with your RAG system
   - 8 columns matching your original dataset structure

2. **cleaned_funding_synthetic_2010_2025_extended.csv** (3.0 MB)
   - Extended version with additional metadata
   - Includes funding stage, quarter, month, USD amounts

3. **cleaned_funding_synthetic_2010_2025_metadata.json**
   - Dataset statistics and generation metadata

## 📈 Dataset Statistics

### Overall Metrics
- **Total Records**: 23,243 funding events
- **Time Period**: January 2010 - December 2025
- **Unique Companies**: 181 startups
- **Unique Sectors**: 12 industry sectors
- **Unique Cities**: 22 Indian cities
- **States Covered**: 15 states

### Year-wise Distribution
```
2010:    281 deals
2011:    375 deals
2012:    468 deals
2013:    656 deals
2014:    937 deals
2015:  1,218 deals
2016:  1,406 deals
2017:  1,687 deals
2018:  1,875 deals
2019:  2,062 deals
2020:  1,593 deals (COVID impact)
2021:  2,812 deals (funding boom)
2022:  2,343 deals
2023:  1,687 deals (correction)
2024:  1,875 deals
2025:  1,968 deals
```

### Sector Distribution
1. **E-Commerce**: 5,251 deals (22.6%)
2. **Fintech**: 3,819 deals (16.4%)
3. **Edtech**: 2,434 deals (10.5%)
4. **Healthtech**: 2,195 deals (9.4%)
5. **Logistics**: 1,977 deals (8.5%)
6. **Foodtech**: 1,836 deals (7.9%)
7. **Mobility**: 1,575 deals (6.8%)
8. **SaaS**: 1,562 deals (6.7%)
9. **Agritech**: 989 deals (4.3%)
10. **Gaming**: 698 deals (3.0%)
11. **Social Media**: 601 deals (2.6%)
12. **Deeptech**: 306 deals (1.3%)

### Geographic Distribution (Top 10 Cities)
1. Pune: 2,289
2. Mumbai: 2,281
3. Bangalore: 2,264
4. Delhi: 2,194
5. Chennai: 2,192
6. Hyderabad: 2,186
7. Gurgaon: 2,123
8. Ahmedabad: 787
9. Coimbatore: 784
10. Kolkata: 758

### Most Active Companies
1. Cars24: 326 funding rounds
2. FreshToHome: 290 rounds
3. Udaan: 278 rounds
4. DeHaat: 251 rounds
5. CarDekho: 244 rounds

## 🎯 Dataset Features

### Realistic Data Patterns

#### 1. **Historical Funding Trends**
- Early years (2010-2014): Dominated by Tier 1 cities (90%)
- Growth phase (2015-2018): Increased Tier 2 city participation
- Mature phase (2019-2025): More geographic distribution
- 2021 funding bubble with 1.5x multiplier
- 2022-2023 market correction with 0.7x reduction

#### 2. **Sector Evolution**
- E-commerce dominance in early years
- Fintech boom from 2013 onwards
- Edtech surge during 2015-2021
- Agritech emergence from 2016
- Gaming/Social Media growth from 2017

#### 3. **Company Lifecycle Modeling**
- Progressive funding stages (Seed → Series A → B → C...)
- Age-based stage selection
- Multiple funding rounds per company

#### 4. **Realistic Funding Amounts**
- Sector-specific multipliers (E-commerce 1.5x, Agritech 0.7x)
- Year-based adjustments (2021 boom, 2022 correction)
- Log-normal distribution for realistic spread
- Currency conversion using historical INR-USD rates

#### 5. **Investor Categorization**
- **Domestic VCs**: Sequoia India, Accel India, Blume Ventures
- **Foreign VCs**: Tiger Global, SoftBank, Tencent
- **Corporate VCs**: Google Ventures, Amazon Ventures
- **Angels**: Ratan Tata, Kunal Shah, Sachin Bansal
- **PE Funds**: Warburg Pincus, KKR, Blackstone

## 📋 Column Descriptions

### Standard Format (Main CSV)
| Column | Description | Example |
|--------|-------------|---------|
| Startup Name | Company name | Flipkart, Swiggy, BYJU'S |
| Amount_Cleaned | Funding amount in INR | ₹50.25 Cr, ₹5.50 L |
| Sector_Standardized | Industry sector | E-Commerce, Fintech |
| City | City of operation | Bangalore, Mumbai |
| State_Standardized | Indian state | Karnataka, Maharashtra |
| Investors' Name | Investor names (comma-separated) | Sequoia Capital India, Tiger Global |
| Date_Parsed | Funding date | 2021-05-15 |
| Year | Year of funding | 2021 |

### Extended Format (Extended CSV)
Additional columns:
- **Amount_USD**: USD equivalent with conversion rate
- **Amount_INR_Numeric**: Numeric INR value for calculations
- **Funding_Stage**: Seed, Series A/B/C/D/E+, Bridge, Debt, Growth
- **Quarter**: Q1/Q2/Q3/Q4
- **Month**: Full month name

## 🔧 Usage with Your RAG System

### 1. Direct Replacement
```bash
# Replace your old dataset
cp cleaned_funding_synthetic_2010_2025.csv cleaned_funding.csv
```

### 2. Re-index ChromaDB
```python
# Re-run your embedding script
python embed_data.py  # Or your equivalent script
```

### 3. Update Company Cache (Optional)
The dataset includes 181 companies vs your original ~100. You may want to regenerate `company_info_cache.json`.

## 🚀 Real Indian Startups Included

### Unicorns & Soonicorns
- Flipkart, Swiggy, Zomato, BYJU'S, Ola, Oyo, Paytm, PhonePe
- CRED, Razorpay, Zerodha, Dream11, Meesho, Udaan, Zetwerk
- ShareChat, Licious, Blinkit (Grofers), Unacademy, Vedantu

### High-Growth Startups
- Cars24, Spinny, Droom, Delhivery, Shiprocket, Xpressbees
- BharatPe, Jupiter, Slice, Khatabook, OkCredit
- Arya.ag, DeHaat, CropIn, Ninjacart, WayCool

### D2C & Consumer Brands
- Mamaearth, Wow Skin Science, Sugar Cosmetics, Pilgrim
- boAt, Noise, Fire-Boltt, Atomberg, Lenskart

## 📊 Data Quality Metrics

✅ **Completeness**: 100% (no missing values)  
✅ **Consistency**: Standardized formats across all fields  
✅ **Realism**: Based on actual Indian startup ecosystem trends  
✅ **Diversity**: 12 sectors, 22 cities, 181 companies  
✅ **Temporal Coverage**: 15 years of continuous data  

## 🎨 Visualization Ideas

The dataset supports rich analytics:
1. **Year-wise funding trends** (2010-2025 timeline)
2. **Sector heatmaps** (evolution over time)
3. **Geographic concentration** (Tier 1/2/3 distribution)
4. **Company journey** (Seed to Unicorn trajectories)
5. **Investor network** (co-investment patterns)

## 🔄 Regeneration

To generate a new dataset with different random values:

```bash
python synthetic_funding_generator.py
```

You can modify parameters in the script:
- `target_records`: Number of records to generate
- `YEAR_INTENSITY`: Adjust deals per year
- `FUNDING_STAGES`: Modify funding ranges
- `USD_TO_INR`: Update currency rates

## 📝 Notes

1. **Synthetic Data**: While based on real companies and trends, funding amounts and dates are synthetically generated
2. **Realistic Patterns**: Incorporates actual market dynamics (2021 boom, 2022 correction, COVID impact)
3. **RAG Optimized**: Designed for vector similarity search with diverse query patterns
4. **Multilingual Ready**: Compatible with your 8-language system

## 🎯 Perfect For

- **Hackathon Demos**: Impressive scale and realism
- **RAG System Testing**: Complex queries across years/sectors/cities
- **Analytics Showcase**: Rich dataset for visualization
- **Multilingual Queries**: Supports Hindi, Marathi, Tamil, etc.

## 📞 Support

For issues or modifications, edit `synthetic_funding_generator.py` and regenerate.

---

**Generated**: January 5, 2026  
**Format Version**: 1.0  
**Compatible With**: Your multilingual RAG-based startup funding query system
